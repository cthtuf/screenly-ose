from nose.tools import eq_, assert_raises
import screenly_net_mgr


NTP_CONF_STANZA = """# Generated by Screenly Network Manager
driftfile /var/lib/ntp/ntp.drift

statistics loopstats peerstats clockstats
filegen loopstats file loopstats type day enable
filegen peerstats file peerstats type day enable
filegen clockstats file clockstats type day enable
restrict -4 default kod notrap nomodify nopeer noquery
restrict -6 default kod notrap nomodify nopeer noquery

restrict 127.0.0.1
restrict ::1
"""


def test_no_if():
    assert_raises(ValueError, screenly_net_mgr.if_config)


def test_eth0_dhcp():
    eq_(screenly_net_mgr.if_config(
        interface='eth0'
    ), """
auto eth0
  iface eth0 inet dhcp
""")


def test_eth3_dhcp():
    eq_(screenly_net_mgr.if_config(
        interface='eth3'
    ), """
auto eth3
  iface eth3 inet dhcp
""")


def test_eth0_static():
    eq_(screenly_net_mgr.if_config(
        interface='eth0',
        ip='192.168.10.1',
        netmask='255.255.255.0',
        gateway='192.168.10.1'
    ), """
auto eth0
  iface eth0 inet static
  address 192.168.10.1
  netmask 255.255.255.0
  gateway 192.168.10.1
""")


def test_wlan0_dhcp_no_passphrase():
    eq_(screenly_net_mgr.if_config(
        interface='wlan0',
        ssid='foobar'
    ), """
auto wlan0
  iface wlan0 inet dhcp
  wireless-power off
  wpa-ssid foobar
""")


def test_wlan0_dhcp_with_passphrase():
    eq_(screenly_net_mgr.if_config(
        interface='wlan0',
        ssid='foobar',
        passphrase='password'
    ), """
auto wlan0
  iface wlan0 inet dhcp
  wireless-power off
  wpa-ssid foobar
  wpa-psk password
""")


def test_wlan1_dhcp_with_passphrase():
    eq_(screenly_net_mgr.if_config(
        interface='wlan1',
        ssid='foobar',
        passphrase='password'
    ), """
auto wlan1
  iface wlan1 inet dhcp
  wireless-power off
  wpa-ssid foobar
  wpa-psk password
""")


def test_wlan0_static_with_passphrase():
    eq_(screenly_net_mgr.if_config(
        interface='wlan0',
        ssid='foobar',
        passphrase='password',
        ip='192.168.10.1',
        netmask='255.255.255.0',
        gateway='192.168.10.1'
    ), """
auto wlan0
  iface wlan0 inet static
  address 192.168.10.1
  netmask 255.255.255.0
  gateway 192.168.10.1
  wireless-power off
  wpa-ssid foobar
  wpa-psk password
""")


def test_wlan0_dhcp_with_hidden_ssid():
    eq_(screenly_net_mgr.if_config(
        interface='wlan0',
        ssid='foobar',
        passphrase='password',
        hidden_ssid='true',
    ), """
auto wlan0
  iface wlan0 inet dhcp
  wireless-power off
  wpa-ssid foobar
  wpa-psk password
  wpa-ap-scan 1
  wpa-scan-ssid 1
""")


def ifconfig_with_one_dns_server():
    eq_(screenly_net_mgr.if_config(interface='eth0', dns='1.2.3.4'), """
auto eth0
  iface eth0 inet dhcp
  dns-nameservers 1.2.3.4
""")


def ifcconfig_with_two_dns_servers():
    eq_(screenly_net_mgr.if_config(interface='eth0', dns='1.1.1.1, 2.2.2.2'), """
auto eth0
  iface eth0 inet dhcp
  dns-nameservers 1.2.3.4, 2.2.2.2
""")


def test_ntp_conf_without_options():
    ntp_conf = NTP_CONF_STANZA
    for n in range(0, 3):
        s = '{}.pool.ntp.org'.format(n)
        ntp_conf += 'server {} iburst\n'.format(s.lower())

    eq_(screenly_net_mgr.generate_ntp_conf(), ntp_conf)


def test_ntp_conf_with_one_option():
    servers = ['1.2.3.4']
    ntp_conf = NTP_CONF_STANZA
    ntp_conf += 'server {} iburst\n'.format(servers[0])

    eq_(screenly_net_mgr.generate_ntp_conf(ntpservers=servers), ntp_conf)


def test_ntp_conf_with_two_option():
    servers = ['1.1.1.1', '2.2.2.2']
    ntp_conf = NTP_CONF_STANZA

    for n in servers:
        ntp_conf += 'server {} iburst\n'.format(n)

    eq_(screenly_net_mgr.generate_ntp_conf(ntpservers=servers), ntp_conf)


def test_ntp_conf_with_invalid_option():
    eq_(screenly_net_mgr.generate_ntp_conf(ntpservers='foobar'), False)
