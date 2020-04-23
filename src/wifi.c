#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char **argv)
{
   char *wifi_config;
   char *config;
   size_t size;

   // check arguments
   if ( 3 == argc )
      wifi_config = "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\nupdate_config=1\ncountry=ES\n\nnetwork={\n\tssid=\"%s\"\n\tpsk=\"%s\"\n\tkey_mgmt=WPA-PSK\n}";
   else if (2 == argc )
      wifi_config = "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\nupdate_config=1\ncountry=ES\n\nnetwork={\n\tssid=\"%s\"\n\tkey_mgmt=NONE\n}";
   else
      return -1;

   // allocate space and write final config text
   size = snprintf(NULL, 0, wifi_config, argv[1], argv[2]);
   config = (char *)malloc(size + 1);
   snprintf(config, size+1, wifi_config, argv[1], argv[2]);

   // replace wifi config
   FILE *fp = fopen("/etc/wpa_supplicant/wpa_supplicant.conf","w");
   if ( fp == 0 ) {
      printf("Error abriendo fichero.\n");
      return -1;
   }

   fprintf(fp, config);
   fclose(fp);

   return 0;
}