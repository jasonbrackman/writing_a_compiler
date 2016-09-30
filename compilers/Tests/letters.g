/* letters.g */

extern func putchar(c int) int;
var r int;
var counter int = 65;
while counter < 91 {
    r = putchar(counter);
    r = putchar(10);
    counter = counter + 1;
}
