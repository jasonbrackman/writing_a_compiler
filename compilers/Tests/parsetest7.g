// Tests involving array datatypes

var a int[10];          /* Declaration of an array */
var b int[10+20];       /* Array with an expression size */

a[0] = 123;             /* Assignment to an array location */
a[1+2] = 456;

var c int = a[1] + a[2+3];   /* Reading from an array */

a[a[0]] = a[1] + a[a[a[2]]];  /* Nested array access */



