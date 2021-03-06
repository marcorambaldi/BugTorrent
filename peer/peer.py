#!/usr/bin/env python

from utils import net_utils, Logger, shell_colors as shell
from .LocalData import LocalData
from common.ServerThread import ServerThread
from .handler import MenuHandler
from .handler import UploadHandler
from .Menu import Menu
import socket


def startup():

	while True:
		shell.print_blue('\nThis process will allow you to add a tracker.\n')
		tracker = net_utils.prompt_host_request('Insert a known host')
		LocalData.set_tracker(tracker)
		# LocalData.set_tracker(('172.16.1.', 'fc00::1:', 3000))

		# tenta login
		ip = net_utils.get_local_ip_for_response()
		port = str(net_utils.get_peer_port()).zfill(5)
		packet = "LOGI" + ip + port

		tracker_ip4 = LocalData.get_tracker_ip4()
		tracker_ip6 = LocalData.get_tracker_ip6()
		tracker_port = LocalData.get_tracker_port()

		try:
			sock = net_utils.send_packet(tracker_ip4, tracker_ip6, tracker_port, packet)
			response = sock.recv(50).decode()

			if len(response) != 20:
				shell.print_red(f'There was an error in the login process: unexpected: {response}.\nPlease retry.')
				continue

			session_id = response[4:20]

			if session_id == '0' * 16:
				shell.print_red(
					f'There was an error in the login process: unexpected session_id: {session_id}.\nPlease retry.')
				continue

			LocalData.session_id = session_id
			break

		except (socket.error, AttributeError):
			shell.print_yellow(f'Unable to contact {tracker_ip4}|{tracker_ip6} [{tracker_port}]')
			if sock is not None:
				sock.close()
			continue

	shell.print_green(f'Successfully logged to the tracker: {tracker_ip4}|{tracker_ip6} [{tracker_port}]\n')

	log = Logger.Logger('peer/peer.log')

	server = ServerThread(net_utils.get_peer_port(), UploadHandler.UploadHandler(log))
	server.daemon = True
	server.start()

	Menu(MenuHandler.MenuHandler(), server).show()
