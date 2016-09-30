/* mandel_simple.g */

extern func putchar(c int) int;
const xmin = -2.0;
const xmax = 1.0;
const ymin = -1.5;
const ymax = 1.5;
const width = 80.0;
const height = 40.0;
const threshhold = 1000;

var dx float = (xmax - xmin)/width;
var dy float = (ymax - ymin)/height;
var y float = ymax;
var x float;
var r int;
var xt float;
var yt float;
var xtemp float;
var n int;
var in bool;

while y >= ymin {
    x = xmin;
    while x < xmax {
            xt = 0.0;
            yt = 0.0;

            n = threshhold;
            in = true;
            while n > 0 {
                    xtemp = xt*xt - yt*yt + x;
                    yt = 2.0*xt*yt + y;
                    xt = xtemp;
                    n = n - 1;
                    if xt*xt + yt*yt > 4.0 {
                            in = false;
                            n = 0;
                        }
                }
            if in {
                    r = putchar(46);
                } else {
                r = putchar(42);
            }
            x = x + dx;
        }
    r = putchar(10);
    y = y - dy;
}