/* Based on UDP code from ccplusplus.com/2011/08/socket-udp-datagram-client-sample-c.html*/
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>


static void displayError(const char *on_what){
 fputs(strerror(errno), stderr);
 fputs(": ", stderr);
 fputs(on_what, stderr);
 fputc('\n',stderr);
 exit(1);
}

int main(int argc, char **argv) {
 int z;
 int x;
 char *srvr_addr = NULL;
 struct sockaddr_in adr_srvr;
 struct sockaddr_in adr;
 int len_inet;
 int s;
 char dgram[512];

 if (argc >= 2) {
  srvr_addr = argv[1];
 }else{
   srvr_addr = "192.168.1.3";
 }

 memset(&adr_srvr, 0, sizeof adr_srvr);
 
 adr_srvr.sin_family = AF_INET;
 adr_srvr.sin_port = htons(54259);
 adr_srvr.sin_addr.s_addr = htonl(INADDR_ANY);//srvr_addr);


 len_inet = sizeof adr_srvr;
s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
 if ( s <= 0 ) {
   displayError("socket()");
 }

if(bind(s, (struct sockaddr*)&adr_srvr, sizeof(adr_srvr) ) < 0)
{
 displayError("bind");
}
printf("starting recv\n");
 for(;;) {

 z = recvfrom(s, dgram, sizeof dgram, 0, (struct sockaddr *)&adr, &x);
 if (z < 0){
  displayError("recvfrom");
 }
 dgram[z] = 0;
 printf("result from %s port %u :\n\t'%s'\n",
   inet_ntoa(adr.sin_addr),
   (unsigned)ntohs(adr.sin_port),
   dgram);
  }
close(s);
putchar('\n');
return 0;
}
