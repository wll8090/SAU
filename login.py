from ldap3 import Connection, Server, ALL


server=Server('10.253.251.13',get_info=ALL)

conn=Connection(server,'sergio@server.local','@Aa1020')

print(conn.bind())