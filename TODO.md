Look into  Segment Anything Model (SAM) 

<!-- Documentation -->
https://cdn.sparkfun.com/assets/1/4/2/1/9/TFmini_Plus_A02_Product_Manual_EN.pdf

<!-- Dependencies -->
https://github.com/adafruit/Adafruit_CircuitPython_TFmini

Here is the output for test_tfmini.py. I don't think it's working as expected. I move the sensor closer and further from my body and the distance doesn't not change in a significant way. 
(ski) admin@raspberrypi:~/Documents/ski-safety $ python scripts/test_tfmini.py 
TFmini listening on /dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_CAA9o151406-if00-port0 @ 115200. Ctrl+C to stop.
1771541783.921  Distance:   43 cm  Strength: 19801  Temp:   55.0 C
1771541784.021  Distance:   42 cm  Strength: 20023  Temp:   55.5 C
1771541784.122  Distance:   42 cm  Strength: 20344  Temp:   55.0 C
1771541784.222  Distance:   42 cm  Strength: 20637  Temp:   55.0 C
1771541784.322  Distance:   42 cm  Strength: 12629  Temp:   55.0 C
1771541784.422  Distance:   43 cm  Strength:  5362  Temp:   55.0 C
1771541784.523  Distance:   43 cm  Strength:  4693  Temp:   55.2 C
1771541784.623  Distance:   42 cm  Strength:  4642  Temp:   55.0 C
1771541784.723  Distance:   42 cm  Strength:  4661  Temp:   55.0 C
1771541784.823  Distance:   42 cm  Strength:  4656  Temp:   55.0 C
1771541784.923  Distance:   42 cm  Strength:  4639  Temp:   55.0 C
1771541785.024  Distance:   42 cm  Strength:  4584  Temp:   55.0 C
1771541785.124  Distance:   42 cm  Strength:  4517  Temp:   55.0 C
1771541785.224  Distance:   42 cm  Strength:  4456  Temp:   55.0 C
1771541785.324  Distance:   42 cm  Strength:  4439  Temp:   55.0 C
1771541785.425  Distance:   42 cm  Strength:  4432  Temp:   55.0 C
1771541785.525  Distance:   41 cm  Strength:  4439  Temp:   55.0 C
1771541785.625  Distance:   42 cm  Strength:  4451  Temp:   55.0 C
1771541785.725  Distance:   42 cm  Strength:  4464  Temp:   55.0 C
1771541785.825  Distance:   41 cm  Strength:  4493  Temp:   55.0 C
1771541785.926  Distance:   41 cm  Strength:  4534  Temp:   55.0 C
1771541786.026  Distance:   41 cm  Strength:  4599  Temp:   55.0 C
1771541786.126  Distance:   41 cm  Strength:  4670  Temp:   55.0 C
1771541786.227  Distance:   41 cm  Strength:  4729  Temp:   55.0 C
1771541786.327  Distance:   41 cm  Strength:  4775  Temp:   55.0 C
1771541786.427  Distance:   41 cm  Strength:  4854  Temp:   55.0 C
1771541786.528  Distance:   41 cm  Strength:  4936  Temp:   55.0 C
1771541786.628  Distance:   41 cm  Strength:  4995  Temp:   55.0 C
1771541786.728  Distance:   41 cm  Strength:  5051  Temp:   55.0 C
1771541786.829  Distance:   40 cm  Strength:  5105  Temp:   55.0 C
1771541786.929  Distance:   40 cm  Strength:  5140  Temp:   55.0 C
1771541787.030  Distance:   40 cm  Strength:  5132  Temp:   55.0 C
1771541787.130  Distance:   40 cm  Strength:  5087  Temp:   55.0 C
1771541787.230  Distance:   40 cm  Strength:  5059  Temp:   55.0 C
1771541787.330  Distance:   40 cm  Strength:  5047  Temp:   55.0 C
1771541787.430  Distance:   40 cm  Strength:  5016  Temp:   55.0 C
1771541787.531  Distance:   40 cm  Strength:  5007  Temp:   55.0 C
1771541787.631  Distance:   40 cm  Strength:  5037  Temp:   55.0 C
1771541787.731  Distance:   40 cm  Strength:  5061  Temp:   55.0 C
1771541787.831  Distance:   40 cm  Strength:  5056  Temp:   55.0 C
1771541787.931  Distance:   40 cm  Strength:  5078  Temp:   55.0 C
1771541788.032  Distance:   40 cm  Strength:  5088  Temp:   55.0 C
1771541788.132  Distance:   40 cm  Strength:  5099  Temp:   55.0 C
1771541788.232  Distance:   39 cm  Strength:  5078  Temp:   55.0 C
1771541788.332  Distance:   39 cm  Strength:  5052  Temp:   55.0 C
1771541788.432  Distance:   40 cm  Strength:  5057  Temp:   55.0 C
1771541788.533  Distance:   39 cm  Strength:  5071  Temp:   55.0 C
1771541788.633  Distance:   39 cm  Strength:  5102  Temp:   55.0 C
1771541788.733  Distance:   39 cm  Strength:  5127  Temp:   55.0 C
1771541788.833  Distance:   39 cm  Strength:  5148  Temp:   55.0 C
1771541788.933  Distance:   39 cm  Strength:  5144  Temp:   55.0 C
1771541789.033  Distance:   39 cm  Strength:  5123  Temp:   55.0 C
1771541789.134  Distance:   39 cm  Strength:  5123  Temp:   55.0 C
1771541789.234  Distance:   39 cm  Strength:  5106  Temp:   55.0 C
1771541789.334  Distance:   39 cm  Strength:  5102  Temp:   55.0 C
1771541789.434  Distance:   39 cm  Strength:  5130  Temp:   55.0 C
1771541789.535  Distance:   39 cm  Strength:  5166  Temp:   55.0 C
1771541789.635  Distance:   39 cm  Strength:  5214  Temp:   55.0 C
1771541789.736  Distance:   39 cm  Strength:  5250  Temp:   55.0 C
1771541789.837  Distance:   39 cm  Strength:  5285  Temp:   55.0 C
1771541789.937  Distance:   39 cm  Strength:  5317  Temp:   55.0 C
1771541790.037  Distance:   39 cm  Strength:  5335  Temp:   55.0 C
1771541790.137  Distance:   39 cm  Strength:  5347  Temp:   55.0 C
1771541790.238  Distance:   39 cm  Strength:  5352  Temp:   55.0 C
1771541790.338  Distance:   39 cm  Strength:  5346  Temp:   55.0 C
1771541790.438  Distance:   39 cm  Strength:  5349  Temp:   55.0 C
1771541790.538  Distance:   39 cm  Strength:  5320  Temp:   55.0 C
1771541790.638  Distance:   39 cm  Strength:  5275  Temp:   55.0 C
1771541790.738  Distance:   39 cm  Strength:  5200  Temp:   55.0 C
1771541790.839  Distance:   39 cm  Strength:  5137  Temp:   55.0 C
1771541790.939  Distance:   39 cm  Strength:  5094  Temp:   55.0 C
1771541791.039  Distance:   39 cm  Strength:  5052  Temp:   55.0 C
1771541791.139  Distance:   39 cm  Strength:  4991  Temp:   55.0 C
1771541791.239  Distance:   39 cm  Strength:  4938  Temp:   55.0 C
1771541791.340  Distance:   39 cm  Strength:  4942  Temp:   55.0 C
1771541791.440  Distance:   39 cm  Strength:  4964  Temp:   55.0 C
1771541791.540  Distance:   39 cm  Strength:  4966  Temp:   55.0 C
1771541791.640  Distance:   39 cm  Strength:  4935  Temp:   55.0 C
1771541791.741  Distance:   39 cm  Strength:  4880  Temp:   55.0 C
1771541791.841  Distance:   39 cm  Strength:  4813  Temp:   55.0 C
1771541791.941  Distance:   39 cm  Strength:  4752  Temp:   55.0 C
1771541792.041  Distance:   39 cm  Strength:  4717  Temp:   55.0 C
1771541792.141  Distance:   39 cm  Strength:  4722  Temp:   55.0 C
^C