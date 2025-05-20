# myo-nintendo-switch

### Usage:

```
pip install pyomyo==0.0.2
pip install nxbt
```

Note: NXBT needs root privileges to toggle the BlueZ Input plugin.

### 1. Gathering Training Data:

You can gather training data by running `python3 neuro_training_3.py`.  
The first phase involves following the paddle with your hand. The second phase involves opening and closing your fist. This will run for a default of 4 minutes before saving it to `foo.csv` and `bar.csv`.  
**Note that sEMG data, the same kind gathered by the Myo is thought to be uniquely identifiable. Do not share this data without careful consideration of the future implications.**

### 2. Start TUI interface

```
sudo python3 tui_for_myo.py --ip <ip address> --port <port number>
```

### 3. Run Myo Control

In another terminal in parallel, start the myo connection script

```
python3 myo_regression.py --ip <ip address> --port <port number>
```

### 4. Control the Switch

You may use the keyboard interface to navigate throughout the Nintendo Switch. Once you would like to toggle EMG control, press e.

![IMG_7501 (1)](https://github.com/user-attachments/assets/0dfd171a-9783-4489-a007-4ff98b251c01)

### About

Built on top of existing code from [pyomyo](https://github.com/PerlinWarp/pyomyo) [Neurobreakout](https://github.com/PerlinWarp/Neuro-Breakout) and [nxbt](https://github.com/Brikwerk/nxbt).

The sEMG sensor used was a Myo gesture control armband made by Thalmic Labs.  
[The Pygame breakout tutorial used.](https://www.101computing.net/breakout-tutorial-using-pygame-getting-started/)

The code is primarily developed on Linux.

#### Getting data from the Myo

emg_mode.PREPROCESSED (0x01)  
By default myo-raw sends 50Hz data that has been rectified and filtered, using a hidden 0x01 mode.

emg_mode.FILTERED (0x02)  
Alvipe added the ability to also get filtered non-rectified sEMG (thanks Alvipe).

emg_mode.RAW (0x03)  
Then I further added the ability to get true raw non-filtered data at 200Hz. This data is unrectified but scales from -128 and 127.
