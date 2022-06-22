# analog-press
Alternative Analog to Digital (ATD) input for box style controllers which aims to more closely follow traditional analog stick behavior. The code in this repository allows you to visualize your inputs, for both Analog Press and the ATD scheme used in current box-style controllers. To see how Analog Press works, head to [ATD Methodology](#atd-methodology)

## Dependencies
Currently, to run the project you will need to install python. In the future, a packaged app may be released, but getting started with python is very straightforward. I recommed getting started with [VS Code](https://code.visualstudio.com/docs/python/python-tutorial).
You will also need to install [pygame](https://www.pygame.org/wiki/GettingStarted) to run the program.

## General Usage
Run *main.py* to start the program. A window will appear with a grid that visualizes the melee stick coordinates. The squares in grey are values with a distance greater than 1 from the center, and the white squares compose the valid stick coordinates. The red square is the current stick position that is sent to the console. To stop the visualization from running, you can either hit your **ESC** key, or close the window. Pressing keys will cause the cursor to move, in the way defined by the DAC in use.
<p align="center">
  <img src="images/window.png" width="600" height="600">
  <br />Default window appearance
</p>  

## Keybindings
The default keybindings are as follows:
![default keybinds](/images/keyboard-layout.png)
Note that only the buttons necessary to generate or modify coordinate values have been mapped. The keybinds are contained in the *keymap.py* folder. Simply change the variable to the key you wish to use. The names of the pygame constants are available [here](https://www.pygame.org/docs/ref/key.html). 

For example, if I wished to change my notch key from left shift to space bar,
```python
NOTCH = pygame.K_LSHIFT
```
would become
```python
NOTCH = pygame.K_SPACE
```
Note that the **SLOW**, and **HOLD** buttons correspond to **Modifier X** and **Modifier Y** in the standard box input scheme, respectively. 
## Input Selection
In the **update_pos** function in *main.py*, the value **use_boxx** allows you to select which input method to use. When True, it uses the Frame1 implementation, and when False uses Analog Press.

## ATD Methodology
### Frame1 ATD
The ATD input coordinates are taken straight from Arte's pico rectangle firmware [here](https://github.com/JulienBernard3383279/pico-rectangle/blob/master/src/dac_algorithms/melee_F1.cpp). This is based on the current Frame1 DAC, which means there are some nerfs found on the b0xx that are not implemented. If you wish to understand why certain coordinates values were chosen, and the combinations of buttons that yield certain coordinates, you can read the **b0xx SSBM [instruction manual](https://drive.google.com/file/d/1InBmEJkWi3E5ReAUIGM9loHygaoNODcf/view).**

### Analog Press - Motivation
Analog press attempts to make it so that a digital button press behaves more like an analog stick. The current ATD scheme in box controllers maps a combination of buttons to a specific coordinate, allowing for fast consistent inputs. These inputs are generated in a fundamentally different way that how an analog stick creates inputs. This can lead to balance issues, as risks associated with certain stick inputs will never occur on a box. It is possible that relative parity between the current digital and analog controllers can be reached through smart changes and regulations, but it can be difficult to determine the best way to achieve balance. Do you implement travel time nerfs? Add randomness to boxes? Do gamecube controllers need a buff? There are lots of possible solutions, but it can be hard to find an answer that delivers parity between control schemes, while not fundamentally changing the game or upsetting large amounts of the playerbase. By making digital controllers more 'analog', it more closely connects the different styles of controllers, so they are suject to the same risks during gameplay, and makes them more intuitive to balance.

#### How it works
When you press a button during analog press, instead of corresponding to a coordinate, it can be thought of as **pushing the analog stick towards a gate.** When I press up, the control stick travels towards the upwards cardinal. If I press up and right, the control stick travels into the North-East gate. This means that the stick will travel across the coordinate space, and can be polled at any coordinate along its path, just like an analog stick.

When you press in a new direction, the cursor will attempt to move in a straight line from your current coordinate towards the target gate. There are 8 targets, accounting for the 8 possible combinations of button inputs: 4 cardinals and 4 diagonal gates. On an analog stick, you would be able to push the stick straight into the rim at any angle. Unfortunately, since ATD inputs can only have 4 directional buttons (much more than that would be impractical anyway), we are more limited to specifying 8 target points. Even with this limitation, by changing which direction the stick is moving, you will be able to move your cursor to any possible coordinate value.
<p align="center">
  <img src="images/span.gif" width="600" height="600">
  <br />You are able to smoothly move through all coordinates!
</p>  
There is one condition where the stick is not moving in a straight line, and that is when it is <b>rolling between gates</b>. If the stick is at the edge of the coordinate circle and you are moving to an adjacent gate, the control stick will move along the edge of the circle, instead of a straight line. This is important for characters whose recovery moves depend on the distance the stick is from the center. A straight path from gate to gate does not achieve the max distance coordinates. Also, this rolling motion is more akin to how players move an analog stick between gates, increasing the similarity of these input methods. It is also a slight travel time nerf, as rolling along the edge is a slightly longer distance to travel that a straight line (Though not by much). 

<br />This is the general behaviour using the 4 directional buttons. Just like current ATD input, **modifiers** are used to provided additional behaviours to the controller. Note that unlike with current ATD inputs, you can hold multiple modifiers at the same time, and their effects will all still apply.

#### Modifiers - Slow
When you press a button the stick will move quickly towards its target at a constant velocity. It moves quickly because desirable actions like dash require a fast movement from one coordinate to the next. There are times when a slower input is needed, such as initiating a tilt input, or to precisely adjust an angle. To do this, you press the **Slow** modifier. The stick behaviour is the exact same for both the fast and slow movements, all that changes is how quickly they occur.
<br />
<p align="center">
  <img src="images/slow.gif" width="600" height="600">
  <br />Comparing slow and fast stick movement
</p> 

#### Modifiers - Hold
The way this system is designed, when pressing a button, the cursor is constantly in motion. If you let go of all the buttons, then the cursor returns to neutral (think of it as letting go of the stick). This presents a challenge. What if I want to hold my stick at a certain position? Say I want to hold a slight DI coordinate, or I think I have reached the angle I want, but need to wait slightly longer to become actionable and use the angle. To hold the stick at its current position, press the **hold** button, which will freeze the cursor at the current coordinate. It will be frozen for as long as *hold* is pressed, and **at least one direction button is pressed.** If you fully let go of all directions, the stick will return to neutral, and you will not be able to input any other directions until you release *hold*. If you release *hold* at any point, then the cursor will once again move in the direction of your current input.
<br />
<p align="center">
  <img src="images/hold.gif" width="600" height="600">
  <br />Holding in certain coordinates
</p> 

#### Modifiers - Notch
Most boxes only have 2 dedicated modifier buttons, but I experimentally wanted to add notch funtionality. If your cursor is currently against the rim, and rolling from a diagonal into an adjacent cardinal, and the **notch** button is pressed, the cursor will be stopped at the notch value. This allows for the targetting of desirable coordinates along the edge, much like a modified Gamecube Controller shell. 8 notch values are permitted, allowing Analog Press to target 16 coordinates (4 cardinals, 4 diagonals, 8 notches).

<p align="center">
  <img src="images/notch.gif" width="600" height="600">
  <br />Rolling the stick into a notch
</p> 
By default, the notches are set to the maximum allowable angles under the Smash World Tour ruleset <b>(0.9125,0.3875).</b> Certain characters might want other values. You can adjust the notch coordinates to see this in the visualization by changing the coordinates here in these line of code in <i>dac.py</i>.  

```python
if ((current_region == 2 or current_region == 4) and target_region == 3) or ((current_region == 6 or current_region == 8) and target_region == 7):
  notch_p = region_coords(current_region,Point(31,73))
else:
  notch_p = region_coords(current_region,Point(73,31))
```

<br />This is a modifier that I am concerned of balance-wise. Being able to pinpoint values is one of the current ways digital controllers have an advantage over analog. This absolute precision removes the risk when trying to target specific coordinates. While modder notches do exist, They are not as consistent as having a perfect digital value. There are already limitations on notch values, but perhaps this can be explored to ensure balance. Additionally, 3 modifier buttons might lead to challenges with regards to layout. Pressing multiple modifiers at once might also be ergonomically challenging.

#### Other Digital to Analog buttons
This input scheme is only designed with the Left Stick in mind. I don't think this would work as well on the C Stick, and there is probably a better solution. I understand that there are some who think a digital C Stick also provides an advantage over one that is analog, but I don't know enough about the topic to comment on if, or how it should be balanced. As such, this ATD input was never meant to apply to the C Stick, and perhaps there is a better way to handle that input(if it needs it at all). It might be good to use the ideas presented here as a starting point.

<br />The same is true for analog shields. You would still need the current lightshield/mediumshield buttons to get analog values. I think that if you wished to include a notch modifier, it could replace the medium shield button, such that existing controllers do not need to add more buttons.

#### Parity
The aim of a more 'analog' ATD input is to avoid the balance issues created by more 'digital' input schemes. I think that it accomplishes this, and this can be seen by looking at travel time and consistency. However there are still some disparities that need to be understood and addressed, so balance is maintained.

<br />The stick moves with a constant velocity. Currenly there are 3 possible velocities. When it undergoes 'fast' movements, 'slow' movements, and when the stick returns to neutral. Obviously, a physical stick will move with a large variety of speeds, but it isn't feasible to implement such complexity. The ATD method should be simple, but move in a way you might expect a player to be able to move the stick. The current velocities were chosed semi-aribtrarily to allow for standard techniques like dash, walk, pivots and others to be performed. To improve this, basing the stick velocities off of measured results would help to maintain parity. This way, the stick would not be able to move faster than a human can move a stick. Maybe you need more than 3 velocities to create a fair representation of an analog stick! For example, a velocity for when the stick is being rolled along the rim is something I considered - I thought rolling would be slower than smashing the stick side to side. Even in its current state, the stick moves much more like a Gamecube Controller than any rectangle does.

<br />Coordinates are used as targets for stick position, which allows for specific values to be pinpointed. The coordinates are the cardinals and diagonals, which can also be targetted on the Gamecube controller because of the octagonal gates. On the Gamecube controller, due to sensor noise and error in the alignment of the stickbox and the shell, it is hard (sometimes impossible) to consistently achieve perfect **cardinals (0.0, 1.0)** or **diagonals (0.7,0.7)**. While a DTA result will always be more precise, the added precision does not present a significant advantage in this case. A traditional controller can target these values approximately, and because the range of values that generate in-game outputs are large enough at the gates (This had to be fixed in some cases with UCF), having more precision does not create a meaningful advantage. 1.0 cardinal is something to consider, however that is a separate discussion and can be easily implemented. I mentioned notches above, and how digital precision might be too strong with regards to angles.

<br /> There are still some disparities, resulting in techniques being much easier to perform than on a Gamecube Controller. For example, pivot tilts are easy; you just need to press the direction you wish to tilt, along with the slow modifier to get your tilt input (pivoting is the challenging part of the technique). Dashback out of crouch is straighforward, because you roll the stick from down to the side (Press down. While still holding down press to the side. Let go of down). The speed at which the stick makes it easy to perform. With some consideration, I think these can be balanced as well. If the ATD input is designed to work like an analog stick, then in theory it should have the same capabilites as an analog stick. The design just needs to provide a close enough analogue. Balance is obviously top of mind. A new ATD input cannot solve the concerns of current inputs but then create new concerns at the same time.

## Contributing
I'm sure people have plenty of thoughts on how to improve balance. I welcome it! Because of some of the disparities mentioned above I do think it is **much stronger than a controller currently**. I do not have the expertise to fully balance the system by myself, nor do I want to do all the work. Please, experiment with the code to make it fair and intuitive to use. Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html)
