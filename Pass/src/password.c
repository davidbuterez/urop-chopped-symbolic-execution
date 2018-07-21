#include <stdio.h>
#include <string.h>

void a1(int);
void a2(int);

int get_length(const char *str) {
  return strlen(str);
}

void append_string(char *str) {
  strcat(str, "newlyappended");
}

void a1(int x) {
  printf("Yes");
  a2(0);
}

void a2(int y) {
  printf("No");
  a1(0);
}

int check_password(char *buf) {
  int len = get_length(buf);

  if (buf[0] == 'h' && buf[1] == 'e' &&
      buf[2] == 'l' && buf[3] == 'l' &&
      buf[4] == 'o')
    return 1;

  append_string(buf);

  return 0;
}

int main(int argc, char **argv) {
  if (argc < 2)
     return 1;

  int x = get_length(argv[1]);
  
  if (check_password(argv[1])) {
    printf("Password found!\n");
    return 0;
  }

  return 1;
}