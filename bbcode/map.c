#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdint.h>
#include <sys/mman.h>
#include <unistd.h>
#include <ncurses.h>
#define CM_PER_REG_START 0x44e00000
#define CM_PER_REG_LENGTH 1024
#define CM_PER_EPWMSS0_CLKCTRL_OFFSET 0xd4
#define CM_PER_EPWMSS1_CLKCTRL_OFFSET 0xcc
#define CM_PER_EPWMSS2_CLKCTRL_OFFSET 0xd8

#define EPWMSS2_REG_START 0x48304000
#define EQEP_OFFSET 0x180
#define EQEP_REG_LENGTH 0x60
#define QPOSCNT 0x0
#define QPOSINIT 0x4
#define QPOSMAX 0x8
#define QPOSCMP 0xc
#define QPOSILAT 0x10
#define QPOSSLAT 0x14
#define QPOSLAT 0x18
#define QUTMR 0x1c
#define QUPRD 0x20
#define QWDTMR 0x24
#define QWDPRD 0x26
#define QDECCTL 0x28
#define QEPCTL 0x2a
#define QCAPCTL 0x2c
#define QPOSCTL 0x2e
#define QEINT 0x30
#define QFLG 0x32
#define QCLR 0x34
#define QFRC 0x36
#define QEPSTS 0x38
#define QCTMR 0x3a
#define QCPRD 0x3c
#define QCTMRLAT 0x3e
#define QCPRDLAT 0x40
#define REVID 0x5c
//#define EQEP2_REG_START 0x48304180
//#define EQEP2_REG_START 0x44e00000
#define EPWMSS_REG_LENGTH 0x1ff
#define PWM_CLOCK_ENABLE 0x2
#define PWM_CLOCK_DISABLE 0x0

#define PWM_LIST_MAX 3

int PWM_OFFSETS[PWM_LIST_MAX] = {
  CM_PER_EPWMSS0_CLKCTRL_OFFSET / sizeof (uint32_t),
  CM_PER_EPWMSS1_CLKCTRL_OFFSET / sizeof (uint32_t),
  CM_PER_EPWMSS2_CLKCTRL_OFFSET / sizeof (uint32_t)
};

void print_usage (const char *message)
{
  if (message)
    printf ("%s\n", message);

  printf ("pwm_clock <-e | -d> <PWM [PWM]>\n\n");
}

int main (int argc, char **argv)
{
  int i;
  int *cur_list = NULL;
  int *cur_list_index = NULL;
  int enable_list[PWM_LIST_MAX];
  int enable_list_index = 0;
  int disable_list[PWM_LIST_MAX];
  int disable_list_index = 0;
  int dev_mem_fd;
  int count;
  int last_count;
  volatile uint32_t *cm_per_regs;
  volatile uint32_t *eqep2_regs;
  for (i = 0; i < PWM_LIST_MAX; ++i) {
    enable_list[i] = -1;
    disable_list[i] = -1;
  }

  for (i = 1; i < argc; ++i) {
    if (strncmp (argv[i], "-e", 2) == 0) {
      cur_list = enable_list;
      cur_list_index = &enable_list_index;
    }
    else if (strncmp (argv[i], "-d", 2) == 0) {
      cur_list = disable_list;
      cur_list_index = &disable_list_index;
    }
    else {
      if (!cur_list) {
        print_usage (0);
        return 1;
      }

      if (*cur_list_index >= PWM_LIST_MAX) {
        print_usage ("Too many PWM's specified for an option");
        return 1;
      }

      cur_list[*cur_list_index] = atoi (argv[i]);
      ++*cur_list_index;
    }
  }

  dev_mem_fd = open ("/dev/mem", O_RDWR);
  if (dev_mem_fd == -1) {
    perror ("open failed");
    return 1;
  }
#if 0
  cm_per_regs = (volatile uint32_t *)mmap (NULL, CM_PER_REG_LENGTH,
    PROT_READ | PROT_WRITE, MAP_SHARED, dev_mem_fd, CM_PER_REG_START);
        if (cm_per_regs == (volatile uint32_t *)MAP_FAILED) {
    perror ("mmap failed");
    close (dev_mem_fd);
    return 1;
  }

  for (i = 0; i < PWM_LIST_MAX && enable_list[i] != -1; ++i) {
    if (enable_list[i] < 0 || enable_list[i] >= PWM_LIST_MAX) {
      printf ("Invalid PWM specified, %d\n", enable_list[i]);
      goto out;
    }

    printf ("Enabling PWM %d\n", enable_list[i]);
    cm_per_regs[PWM_OFFSETS[enable_list[i]]] = PWM_CLOCK_ENABLE;
  }

  for (i = 0; i < PWM_LIST_MAX && disable_list[i] != -1; ++i) {
    if (disable_list[i] < 0 || disable_list[i] >= PWM_LIST_MAX) {
      printf ("Invalid PWM specified, %d\n", disable_list[i]);
      goto out;
    }

    printf ("Disabling PWM %d\n", disable_list[i]);
    cm_per_regs[PWM_OFFSETS[disable_list[i]]] = PWM_CLOCK_DISABLE;
  }
#endif
  eqep2_regs = (volatile uint32_t *)mmap (NULL, EPWMSS_REG_LENGTH,
    PROT_READ | PROT_WRITE, MAP_SHARED, dev_mem_fd, EPWMSS2_REG_START);
        if (eqep2_regs == (volatile uint32_t *)MAP_FAILED) {
    perror ("mmap failed");
    close (dev_mem_fd);
    return 1;
  }
 eqep2_regs[(EQEP_OFFSET+QDECCTL)>>2] = 0x808A0000;
 eqep2_regs[(EQEP_OFFSET+QCAPCTL)>>2] = 0x0;
 eqep2_regs[(EQEP_OFFSET+QPOSCTL)>>2] = 0x0;
 eqep2_regs[(EQEP_OFFSET+QEINT)>>2] = 0x0;
 printf("wrote to %d\n",(EQEP_OFFSET+QDECCTL)>>2);
	for(i = 0; i < EPWMSS_REG_LENGTH/4; i++){
	printf("%d %x\n",i,eqep2_regs[i]);
	}
  for(i = 0; i < EQEP_REG_LENGTH/4; i++){
	printf("%d %x %x\n",(EQEP_OFFSET >> 2) + i,i<<2,eqep2_regs[(EQEP_OFFSET >> 2) + i]);
	}
count = last_count = eqep2_regs[(EQEP_OFFSET+QPOSCNT)>>2];
printf("count: %x\n",count);
timeout(0);

while(1)
{
 int c = getch();
 if ( c == 27)
 {
   break;
 }
 
count =  eqep2_regs[(EQEP_OFFSET+QPOSCNT)>>2];
if(count!=last_count){
printf("count: %x\n",count);
last_count = count;
}

}

out:
  munmap ((void *)cm_per_regs, CM_PER_REG_LENGTH);
  close (dev_mem_fd);

  return 0;
}
