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
#define PWM_CLOCK_ENABLE 0x2
#define PWM_CLOCK_DISABLE 0x0

#define EPWMSS1_REG_START 0x48302000
#define EPWMSS2_REG_START 0x48304000
#define EPWMSS_REG_LENGTH 0x4000	/* Encapsulates 0x4830_2000 to 0x4830_5fff for pwm1 and pwm 2 */
#define EQEP1_OFFSET 0x180	/* Relative to EPWMSS1_REG_START */
#define EQEP2_OFFSET 0x2180	/* Relative to EPWMSS1_REG_START */
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

#define PWM_LIST_MAX 3

int PWM_OFFSETS[PWM_LIST_MAX] = {
  CM_PER_EPWMSS0_CLKCTRL_OFFSET / sizeof (uint32_t),
  CM_PER_EPWMSS1_CLKCTRL_OFFSET / sizeof (uint32_t),
  CM_PER_EPWMSS2_CLKCTRL_OFFSET / sizeof (uint32_t)
};

void
print_usage (const char *message)
{
  if (message)
    printf ("%s\n", message);

  printf ("pwm_clock <-e | -d> <PWM [PWM]>\n\n");
}

int
main (int argc, char **argv)
{
  int i, eq;
  int *cur_list = NULL;
  int *cur_list_index = NULL;
  int enable_list[PWM_LIST_MAX];
  int enable_list_index = 0;
  int disable_list[PWM_LIST_MAX];
  int disable_list_index = 0;
  int dev_mem_fd;
  int count, count2;
  int last_count, last_count2;
  int eqep_offset_list[2] = { EQEP1_OFFSET, EQEP2_OFFSET };
  int eqep_offset;
  volatile uint32_t *cm_per_regs;
  volatile uint32_t *eqep_regs;
  for (i = 0; i < PWM_LIST_MAX; ++i)
    {
      enable_list[i] = -1;
      disable_list[i] = -1;
    }

  /* Enable Clocks to PWM modules 1 and 2 */
  enable_list[0] = 1;
  enable_list[1] = 2;
  /* data4 and data5: mode3 = eqep_in */
  i = system("echo 23 > /sys/kernel/debug/omap_mux/lcd_data4"); /* eqep2a_in = gpio2_10 = p8-41 */
  i = system("echo 23 > /sys/kernel/debug/omap_mux/lcd_data5"); /* eqep2b_in = gpio2_11 = p8-42 */
  
 /* uart4: mode2 = eqep_in */
i = system("echo 22 > /sys/kernel/debug/omap_mux/lcd_data12"); /* eqep1a_in = gpio0_8 = p8-35 */
  i = system("echo 22 > /sys/kernel/debug/omap_mux/lcd_data13"); /* eqep1b_in = gpio0_9 = p8-33 */
  /* Open memory map */
  dev_mem_fd = open ("/dev/mem", O_RDWR);
  if (dev_mem_fd == -1)
    {
      perror ("open failed");
      return 1;
    }
#if 1
  /* Create memory object */
  cm_per_regs = (volatile uint32_t *) mmap (NULL, CM_PER_REG_LENGTH,
					    PROT_READ | PROT_WRITE,
					    MAP_SHARED, dev_mem_fd,
					    CM_PER_REG_START);
  if (cm_per_regs == (volatile uint32_t *) MAP_FAILED)
    {
      perror ("mmap failed");
      close (dev_mem_fd);
      return 1;
    }

  for (i = 0; i < PWM_LIST_MAX && enable_list[i] != -1; ++i)
    {
      if (enable_list[i] < 0 || enable_list[i] >= PWM_LIST_MAX)
	{
	  printf ("Invalid PWM specified, %d\n", enable_list[i]);
	  goto out;
	}

      printf ("Enabling PWM %d\n", enable_list[i]);
      cm_per_regs[PWM_OFFSETS[enable_list[i]]] = PWM_CLOCK_ENABLE;
    }

  munmap ((void *) cm_per_regs, CM_PER_REG_LENGTH);
#endif

  eqep_regs = (volatile uint32_t *) mmap (NULL, EPWMSS_REG_LENGTH,
					  PROT_READ | PROT_WRITE, MAP_SHARED,
					  dev_mem_fd, EPWMSS1_REG_START);
  if (eqep_regs == (volatile uint32_t *) MAP_FAILED)
    {
      perror ("mmap failed");
      close (dev_mem_fd);
      return 1;
    }
  for (eq = 0; eq < 2; eq++)
    {
      eqep_offset = eqep_offset_list[eq];
      eqep_regs[(eqep_offset + QPOSMAX) >> 2] = 0xFFFFFFFF;
      eqep_regs[(eqep_offset + QPOSINIT) >> 2] = 0xDEADBEEF;
      eqep_regs[(eqep_offset + QUPRD) >> 2] = 100000;
      eqep_regs[(eqep_offset + QDECCTL) >> 2] = 0x808A0000;
      eqep_regs[(eqep_offset + QCAPCTL) >> 2] = 0x0;
      eqep_regs[(eqep_offset + QPOSCTL) >> 2] = 0x0;
      eqep_regs[(eqep_offset + QEINT) >> 2] = 0x0;
      printf ("wrote to %d\n", (eqep_offset + QDECCTL) >> 2);
      for (i = 0; i < EQEP_REG_LENGTH / 4; i++)
	{
	  printf ("%d %x %x\n", (eqep_offset >> 2) + i, i << 2,
		  eqep_regs[(eqep_offset >> 2) + i]);
	}

    }
  count = last_count = eqep_regs[(EQEP1_OFFSET + QPOSCNT) >> 2];
  count2 = last_count2 = eqep_regs[(EQEP2_OFFSET + QPOSCNT) >> 2];
  printf ("count: %x %x\n", count,count2);
  timeout (0);

  while (1)
    {
      int c = getch ();
      if (c == 27)
	{
	  break;
	}

      count = eqep_regs[(EQEP1_OFFSET + QPOSCNT) >> 2];
      count2 = eqep_regs[(EQEP2_OFFSET + QPOSCNT) >> 2];
	if (count != last_count || count2 != last_count2)
	{
	  printf ("count: %x %x\n", count,count2);
	  last_count = count;
	  last_count2 = count2;
	}

    }

out:
  munmap ((void *) cm_per_regs, CM_PER_REG_LENGTH);
  close (dev_mem_fd);

  return 0;
}
