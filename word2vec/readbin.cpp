// Note:
// Code from http://stackoverflow.com/questions/27324292/convert-word2vec-bin-file-to-text
// readfile line by line to avoid the requirement of large 
/* example output
2in 0.052956 0.065460 0.066195 0.047072 0.052221 -0.082009 -0.061415 -0.116210 0.015629 0.099293 -0.085686 -0.028133 0.052221 0.058840 -0.077596 -0.073550 0.033282 0.077228 -0.045785 -0.027214 -0.034201 0.035672 -0.090835 -0.048175 0.001701 0.027949 -0.002195 0.088628 0.046521 0.048175 0.061047 -0.051853 -0.016089 0.041556 -0.064357 0.051853 -0.096351 -0.025007 0.074286 0.132391 0.083480 -0.026110 -0.035488 -0.006390 0.027030 0.077596 0.020318 -0.021605 -0.003861 0.080170 0.045050 0.070976 0.025375 -0.020410 -0.070976 0.000776 -0.036407 0.025926 0.061047 -0.085318 -0.066931 0.027030 -0.109590 -0.183876 -0.046337 0.039901 0.042843 0.135333 0.045969 0.065460 0.093409 -0.030340 0.017009 0.133862 -0.022341 -0.022341 0.088260 0.023444 -0.072447 0.050014 0.003540 -0.060311 0.047440 -0.015538 -0.041188 -0.102235 -0.047808 0.062886 -0.048175 0.016181 0.058105 -0.027949 -0.025375 -0.138275 -0.054795 0.011952 0.070241 -0.046337 -0.010711 -0.002597 0.008366 -0.119152 -0.012871 0.004666 -0.006574 -0.060679 -0.011492 -0.066195 0.002620 -0.012136 -0.009286 0.073550 -0.105177 -0.064724 -0.020226 0.040637 0.100028 0.084951 0.091202 0.064357 -0.005355 0.033649 -0.109590 -0.002413 -0.088628 -0.049279 0.053692 -0.070976 -0.022801 0.090467 0.060311 -0.071344 -0.122094 -0.058473 0.015997 -0.061415 0.002965 -0.118416 -0.073918 0.029972 0.029604 -0.006849 0.077596 0.051117 -0.032178 0.047808 -0.036959 0.015721 -0.125771 0.070241 0.070608 0.005172 0.040453 0.039533 -0.018388 -0.024455 -0.046337 -0.004183 0.072447 0.028501 0.009194 -0.033098 -0.005631 0.079434 0.015354 0.109590 0.061782 0.004344 0.003448 -0.069873 -0.104441 -0.043211 -0.038798 -0.098557 -0.105177 -0.015446 -0.020410 0.024639 0.079067 -0.001758 -0.017009 0.000379 -0.083480 0.063989 -0.097822 -0.013147 -0.000270 0.081273 0.066931 0.033649 0.018939 0.017928 0.061047 0.017836 -0.082744 0.004045 -0.013331 -0.025559 -0.024823 -0.123565 0.072079 -0.013791 0.003999 -0.025926 -0.033282 -0.050014 -0.013515 -0.022341 -0.005723 -0.038614 -0.040820 0.067299 -0.054059 0.011492 -0.062150 -0.023904 0.026846 -0.015997 -0.044682 -0.009837 0.035304 0.017376 0.015813 -0.059208 -0.006068 0.014710 -0.004183 0.031259 0.020962 0.010251 0.026110 -0.137539 0.090467 0.055898 -0.030891 -0.007493 0.032362 -0.005493 0.092673 0.043395 -0.040269 -0.024272 -0.006849 -0.035120 0.033098 -0.038246 0.051853 0.002252 -0.003149 -0.033282 0.055530 -0.009608 0.050750 0.004735 0.056634 -0.028501 0.003678 0.033649 -0.050750 0.007309 0.003563 0.015446 0.053692 0.128713 0.130920 0.041924 0.068770 -0.028133 0.037511 -0.029604 0.033282 0.047072 0.036591 -0.040085 0.036775 -0.098557 -0.021789 -0.027214 -0.045785 -0.043211 0.092673 -0.062150 -0.008964 0.094144 0.001023 0.048175 -0.080170 -0.108119 -0.031811 0.018112 -0.127242 -0.066931 -0.060679 0.048911 0.046153 -0.035672 -0.044314 -0.035856 0.010895 -0.047072 

*/
//  Copyright 2013 Google Inc. All Rights Reserved.
//
//  Licensed under the Apache License, Version 2.0 (the "License");
//  you may not use this file except in compliance with the License.
//  You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
//  Unless required by applicable law or agreed to in writing, software
//  distributed under the License is distributed on an "AS IS" BASIS,
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  See the License for the specific language governing permissions and
//  limitations under the License.

#include <stdio.h>
#include <string.h>
#include <math.h>
#include <malloc.h>

const long long max_size = 2000;         // max length of strings
const long long N = 40;                  // number of closest words that will be shown
const long long max_w = 50;              // max length of vocabulary entries

int main(int argc, char **argv) {
  FILE *f;
  char file_name[max_size];
  float len;
  long long words, size, a, b;
  char ch;
  float *M;
  char *vocab;
  if (argc < 2) {
    printf("Usage: ./distance <FILE>\nwhere FILE contains word projections in the BINARY FORMAT\n");
    return 0;
  }
  strcpy(file_name, argv[1]);
  f = fopen(file_name, "rb");
  if (f == NULL) {
    printf("Input file not found\n");
    return -1;
  }
  fscanf(f, "%lld", &words);
  fscanf(f, "%lld", &size);
  vocab = (char *)malloc((long long)words * max_w * sizeof(char));
  float *Mchar;
  Mchar = (float *)malloc((long long)size * sizeof(float));
  for (b = 0; b < words; b++) {
    fscanf(f, "%s%c", &vocab[b * max_w], &ch);
    printf("%s ",&vocab[b * max_w]);
    for (a = 0; a < size; a++) fread(&Mchar[a], sizeof(float), 1, f);
    len = 0;
    for (a = 0; a < size; a++) len += Mchar[a] * Mchar[a];
    len = sqrt(len);
    for (a = 0; a < size; a++) Mchar[a] /= len;
    for (a = 0; a< size; a++){ printf("%f ",Mchar[a]); }

    printf("\n");
  }
  fclose(f);
  return 0;
}
