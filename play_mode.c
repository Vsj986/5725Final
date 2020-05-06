//play mode

// need for rand function
#include <stdlib.h>
// need for sine function
#include <math.h>
// The fixed point types
#include <stdfix.h>
////////////////////////////////////
#include <stdio.h>
#include <errno.h>
#include <wiringPiI2C.h>


// string buffer
char buffer[60];

short reco_buff[32];
//////////////////////A3     B3      C4     D4     E4      F4    G4
short freq_table[] = {220.00,246.94,261.63,293.66,329.63,349.23,392.00,
///////////////////// A4      B4      C5    D5      E5     F5     G5    A5     B5
                      440.00,493.88,523.25,587.33,659.25,698.46,783.99,880.00,987.77};
short replay;

#define IDLE 0
#define RELEASE 1
short curr_state = 0;

#define PLAY_MODE 0
#define RECO_MODE 1
short curr_mode = 0;

#define NOT_PUSHED 0
#define MAYBE_PUSHED 1
#define PUSHED 2
#define MAYBE_NOT_PUSHED 3
short curr_debounce;

#define freq_button 0xfe
#define reco_button 0xfd
//
// ////////////////////////////////////
// // Audio DAC ISR
// // A-channel, 1x, active
// #define DAC_config_chan_A 0b0011000000000000
// // B-channel, 1x, active
// #define DAC_config_chan_B 0b1011000000000000

// audio sample frequency
#define Fs 44000.0
// need this constant for setting DDS frequency
#define two32 4294967296.0 // 2^32
// sine lookup table for DDS
#define sine_table_size 256
volatile _Accum sine_table[sine_table_size];
// phase accumulator for main DDS
volatile unsigned int DDS_phase;
volatile unsigned int DDS_phase_fm;
// phase increment to set the frequency DDS_increment = Fout*two32/Fs
// For A above middle C DDS_increment =  = 42949673 = 440.0*two32/Fs
float Fout;
// waveform amplitude
volatile _Accum max_amplitude=2000;

// waveform amplitude envelope parameters
// rise/fall time envelope 44 kHz samples
volatile unsigned int attack_time=250, decay_time=50000, sustain_time=0;
volatile unsigned int attack_time_fm=2000, decay_time_fm=40000, sustain_time_fm=0;
//  0<= current_amplitude < 2048
volatile _Accum current_amplitude;
volatile _Accum current_amplitude_fm;
// amplitude change per sample during attack and decay
// no change during sustain
volatile _Accum attack_inc, decay_inc;
volatile _Accum attack_inc_fm, decay_inc_fm;

//== Timer 2 interrupt handler ===========================================
volatile unsigned int DAC_data;// output values

// interrupt ticks since beginning of song or note
volatile unsigned int song_time, note_time;

void __ISR(_TIMER_2_VECTOR, ipl2) Timer2Handler(void)
{
  int junk;

  mT2ClearIntFlag();

  volatile unsigned int DDS_increment = Fout*two32/Fs; //42949673;

  // generate  sinewave
  // advance the phase
  DDS_phase += DDS_increment;

  if (curr_mode == PLAY_MODE) {
  // F_FM is 1.5*F_Main
  DDS_phase_fm += (int)(1.5*DDS_increment);
  int FM_OUT = current_amplitude_fm*sine_table[DDS_phase_fm>>24];
  // sin(x+sin(y))
  DDS_phase += DDS_increment+(FM_OUT<<16);
  DAC_data = (int)(current_amplitude*sine_table[DDS_phase>>24])+2048;

  // update amplitude envelope for main frequency
  if (note_time < (attack_time + decay_time + sustain_time)){
    current_amplitude = (note_time <= attack_time)?
    current_amplitude + attack_inc :
    (note_time <= attack_time + sustain_time)? current_amplitude:
    current_amplitude - decay_inc;
  }
  else {
    current_amplitude = 0;
  }

  // update amplitude envelope for FM frequency
  if (note_time < (attack_time_fm + decay_time_fm + sustain_time_fm)){
    current_amplitude_fm = (note_time <= attack_time_fm)?
    current_amplitude_fm + attack_inc_fm :
    (note_time <= attack_time_fm + sustain_time_fm)? current_amplitude_fm:
    current_amplitude_fm - decay_inc_fm;
  }
  else {
    current_amplitude_fm = 0;
  }


  // record mode for later
  //if(Fout==0 || curr_mode == RECO_MODE) DAC_data = 0;

/////// see if need to do anything here

  // // test for ready
  // while (TxBufFullSPI2());
  //
  // // reset spi mode to avoid conflict with expander
  // SPI_Mode16();
  // // DAC-A CS low to start transaction
  // mPORTBClearBits(BIT_4); // start transaction
  //  // write to spi2
  // WriteSPI2(DAC_config_chan_A | (DAC_data_A & 0xfff));
  //
  // // fold a couple of timer updates into the transmit time
  song_time++;
  note_time++;
  // // test for done
  // while (SPI2STATbits.SPIBUSY); // wait for end of transaction
  // // MUST read to clear buffer for port expander elsewhere in code
  // junk = ReadSPI2();
  // // CS high
  // mPORTBSetBits(BIT_4); // end transaction
  // // DAC-B CS low to start transaction
  // mPORTBClearBits(BIT_4); // start transaction
  // // write to spi2
  // WriteSPI2(DAC_config_chan_B | (DAC_data_B & 0xfff));
  // // test for done
  // while (SPI2STATbits.SPIBUSY); // wait for end of transaction
  // // MUST read to clear buffer for port expander elsewhere in code
  // junk = ReadSPI2();
  // // CS high
  // mPORTBSetBits(BIT_4); // end transaction

  //to do: write to i2c
  using namespace std;
  int fd, result;
  fd = wiringPiI2CSetup(0x60);
  result = wiringPiI2CWriteReg16(fd, 0x40, (DAC_data & 0xfff) );
  if(result == -1)
  {
     printf("Errno is: %s\n", errno);
  }
}

// === thread structures ============================================
// thread control structs
static struct pt pt_timer, pt_key;

// system 1 second interval tick
int sys_time_seconds;
int curr_note;
// === Timer Thread =================================================
// update a 1 second tick counter
// static PT_THREAD (protothread_timer(struct pt *pt))
// {
//   PT_BEGIN(pt);
//   // timer readout
//   sprintf(buffer,"%s", "Time in sec since boot\n");
//   printLine(0, buffer, ILI9340_WHITE, ILI9340_BLACK);
//
//   // set up LED to blink
//   mPORTASetBits(BIT_0); //Clear bits to ensure light is off.
//   mPORTASetPinsDigitalOut(BIT_0);    //Set port as output
//
//   while(1) {
//     // yield time 1 second
//     PT_YIELD_TIME_msec(1000);
//     sys_time_seconds++;
//     // toggle the LED on the big board
//     mPORTAToggleBits(BIT_0);
//
//     // draw sys_time
//     sprintf(buffer,"%d", sys_time_seconds);
//     printLine(1, buffer, ILI9340_YELLOW, ILI9340_BLACK);
//
//     // start a new sound if replaying recorded notes
//     if (curr_mode == PLAY_MODE && replay){
//       note_time = 0;
//       current_amplitude = 0;
//       current_amplitude_fm = 0;
//       int note = reco_buff[curr_note++];
//       Fout = (note>15)? freq_table[note-16]*2 : freq_table[note];
//       if (curr_note==32) curr_note = 0;
//     }
//     // !!!! NEVER exit while !!!!
//   } // END WHILE(1)
//   PT_END(pt);
// } // timer thread

// === Keypad Thread =============================================

static PT_THREAD (protothread_key(struct pt *pt))
{
  PT_BEGIN(pt);
  static int keypad, i, pattern;
  // order is 0 thru 9 then * ==10 and # ==11
  // no press = -1
  // table is decoded to natural digit order (except for * and #)
  // with shift key codes for each key
  // keys 0-9 return the digit number
  // keys 10 and 11 are * adn # respectively
  // Keys 12 to 21 are the shifted digits
  // keys 22 and 23 are shifted * and # respectively
  static int keytable[24]=
  //        0     1      2    3     4     5     6      7    8     9    10-*  11-#
          {0xd7, 0xbe, 0xde, 0xee, 0xbd, 0xdd, 0xed, 0xbb, 0xdb, 0xeb, 0xb7, 0xe7,
  //        s0     s1    s2  s3    s4    s5    s6     s7   s8    s9    s10-* s11-#
           0x57, 0x3e, 0x5e, 0x6e, 0x3d, 0x5d, 0x6d, 0x3b, 0x5b, 0x6b, 0x37, 0x67};
  // bit pattern for each row of the keypad scan -- active LOW
  // bit zero low is first entry
  static char out_table[4] = {0b1110, 0b1101, 0b1011, 0b0111};



  // the read-pattern if no button is pulled down by an output
  #define no_button (0x70)

    while(1) {
      // yield time
      PT_YIELD_TIME_msec(30);
      for (i=0; i<4; i++) {
        start_spi2_critical_section;
        // scan each rwo active-low
        writePE(GPIOY, out_table[i]);
        // reading the port also reads the outputs
        keypad  = readPE(GPIOY);
        end_spi2_critical_section;
        // was there a keypress?
        if((keypad & no_button) != no_button) { break;}
      }

      start_spi2_critical_section;
      // read port Z for the two buttons
      int modeChoice = readPE(GPIOZ);
      end_spi2_critical_section;

      // search for keycode
      if (keypad > 0){ // then button is pushed
        for (i=0; i<24; i++){
          if (keytable[i]==keypad) break;
        }
        // if invalid, two button push, set to -1
        if (i==24) i=-1;
      }
      else i = -1; // no button pushed

      switch (curr_debounce){
        case NOT_PUSHED:
          // if any button pushed
          if (keypad > 0 && i != -1) curr_debounce = MAYBE_PUSHED;
          i = -1;
          break;
        case MAYBE_PUSHED:
          // if any button pushed, impossible to be a different button
          if (keypad > 0 && i != -1) curr_debounce = PUSHED;
          else curr_debounce = NOT_PUSHED;
          break;
        case PUSHED:
          // if not button pushed
          if (keypad <= 0 || i == -1) curr_debounce = MAYBE_NOT_PUSHED;
          break;
        case MAYBE_NOT_PUSHED:
          // if not button pushed
          if (keypad <= 0 || i == -1) curr_debounce = NOT_PUSHED;
          else curr_debounce = PUSHED;
          break;
      }

      int start = 0;

      // draw key number
      if (i>-1 && i<10){
        sprintf(buffer,"   %x %d", keypad, i);
        // assign Fout, disable replay, and start playing the note
        Fout = freq_table[i];
        replay = 0;
        start = 1;
      }
      if (i==10) sprintf(buffer,"   %x *", keypad);
      if (i==11) {
        sprintf(buffer,"   %x #", keypad);
        // enable replay and reset cursor
        replay = 1;
        curr_note = 0;
      }
      if (i>11 && i<22){
        sprintf(buffer, "   %x shift-%d", keypad, i-12);
        // assign Fout, disable replay, and start playing the note
        Fout = freq_table[i-12]*2;
        replay = 0;
        start = 1;
      }
      if (i==22) sprintf(buffer,"   %x ahift-*", keypad);
      if (i==23) sprintf(buffer,"   %x shift-#", keypad);
      if (i>-1 && i<12) printLine2(10, buffer, ILI9340_GREEN, ILI9340_BLACK);
      else if (i>-1) printLine2(10, buffer, ILI9340_RED, ILI9340_BLACK);

      switch (curr_state){
        case IDLE:
          // if any button pressed, start playing/recording and go to RELEASE
          if (start){
            curr_state = RELEASE;
            note_time = 0;
            current_amplitude = 0;
            current_amplitude_fm = 0;
            if (curr_mode == RECO_MODE) reco_buff[curr_note++]=i;
          }
          break;
        case RELEASE:
          // if no button pressed, go back to IDLE
          if (i==-1) curr_state = IDLE;
          break;
      }

      switch (curr_mode){
        case PLAY_MODE:
          if (modeChoice==reco_button){
            // clear the buffer and go to record mode
            memset(reco_buff,0,32);
            curr_note = 0;
            curr_mode = RECO_MODE;
            break;
          }
          if (modeChoice==freq_button) curr_mode = FREQ_MODE;
          break;
        case FREQ_MODE:
          if (modeChoice==reco_button){
            // clear the buffer and go to record mode
            memset(reco_buff,0,32);
            curr_note = 0;
            curr_mode = RECO_MODE;
            break;
          }
          // only in frequency mode if user holds button
          if (modeChoice!=freq_button) curr_mode = PLAY_MODE;
          break;
        case RECO_MODE:
          // only in record mode if user holds button
          if (modeChoice!=reco_button){
            curr_note = 0;
            curr_mode = PLAY_MODE;
          }
          break;
      }
    // !!!! NEVER exit while !!!!
    } // END WHILE(1)
PT_END(pt);
} // keypad thread

// === Main  ======================================================
void main(void) {
  // //SYSTEMConfigPerformance(PBCLK);
  //
  // ANSELA = 0; ANSELB = 0;
  //
  // // set up DAC on big board
  // // timer interrupt //////////////////////////
  // // Set up timer2 on,  interrupts, internal clock, prescalar 1, toggle rate
  // // at 40 MHz PB clock
  // // 40,000,000/Fs = 909 : since timer is zero-based, set to 908
  // OpenTimer2(T2_ON | T2_SOURCE_INT | T2_PS_1_1, 908);
  //
  // // set up the timer interrupt with a priority of 2
  // ConfigIntTimer2(T2_INT_ON | T2_INT_PRIOR_2);
  // mT2ClearIntFlag(); // and clear the interrupt flag
  //
  // // SCK2 is pin 26
  // // SDO2 (MOSI) is in PPS output group 2, could be connected to RB5 which is pin 14
  // PPSOutput(2, RPB5, SDO2);
  //
  // // control CS for DAC
  // mPORTBSetPinsDigitalOut(BIT_4);
  // mPORTBSetBits(BIT_4);
  //
  // // divide Fpb by 2, configure the I/O ports. Not using SS in this example
  // // 16 bit transfer CKP=1 CKE=1
  // // possibles SPI_OPEN_CKP_HIGH;   SPI_OPEN_SMP_END;  SPI_OPEN_CKE_REV
  // // For any given peripherial, you will need to match these
  // // clk divider set to 4 for 10 MHz
  // SpiChnOpen(SPI_CHANNEL2, SPI_OPEN_ON | SPI_OPEN_MODE16 | SPI_OPEN_MSTEN | SPI_OPEN_CKE_REV , 4);
  // // end DAC setup
  //
  // //
  // // build the sine lookup table
  // // scaled to produce values between 0 and 4096
  int i;
  for (i = 0; i < sine_table_size; i++){
    sine_table[i] = (_Accum)(sin((float)i*6.283/(float)sine_table_size));
  }

  // build the amplitude envelope parameters
  // bow parameters range check
  if (attack_time < 1) attack_time = 1;
  if (decay_time < 1) decay_time = 1;
  if (sustain_time < 1) sustain_time = 1;
  // set up increments for calculating bow envelopes for both F_Main and F_FM
  attack_inc = max_amplitude/(_Accum)attack_time;
  decay_inc = max_amplitude/(_Accum)decay_time;
  attack_inc_fm = max_amplitude/(_Accum)attack_time_fm;
  decay_inc_fm = max_amplitude/(_Accum)decay_time_fm;

  // // === config threads ==========
  // // turns OFF UART support and debugger pin, unless defines are set
  // PT_setup();
  //
  // // init the threads
  // PT_INIT(&pt_timer);
  // PT_INIT(&pt_key);
  //
  // // round-robin scheduler for threads
  // while (1){
  //   PT_SCHEDULE(protothread_timer(&pt_timer));
  //   PT_SCHEDULE(protothread_key(&pt_key));
  // }
} // main

// === end ======================================================
