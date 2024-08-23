import config_db
import config_server
import psycopg2
from sshtunnel import SSHTunnelForwarder


def main():
    try:

        tunnel = SSHTunnelForwarder(
            (config_server.server_host, config_server.server_port),
            ssh_username=config_server.ssh_username,
            ssh_password=config_server.ssh_password,
            remote_bind_address=('localhost', 5432),
            local_bind_address=('localhost', 6543),  # could be any available port
        )
        tunnel.start()
        print('[INFO] Tunnel open')

        connection = psycopg2.connect(
            host=tunnel.local_bind_host,
            port=tunnel.local_bind_port,
            user=config_db.user,
            password=config_db.password,
            database=config_db.db_name
        )
        print('[INFO] Connection successful')

        connection.set_session(autocommit=True)

        with connection.cursor() as cursor:

            for i in range(1100, 1101):
                print(f'[INFO] Start iter {i}')

                template = 10000 + i
                user_template_number = ''.join(list(str(template))[1:])
                user_name = 'group4user' + user_template_number
                user_email = user_name + '@wtf.ru'
                user_team_number = 14

                # steps
                # ---------- 1. create new user
                command_new_user = f"insert into boomq_user (user_id, email, password,language, enable_notification, create_date, enabled, display_name) values ((select max(user_id) from boomq_user bu ) + 1,'{user_email}', '\u007bbcrypt\u007d$2a$10$oFyTFabor3T2va4mqs5DxOGeAJ07CEJZCYnwd/dgL/FSfmQuUsbji', 'EN', true, CURRENT_DATE, true, '{user_name}')"
                cursor.execute(command_new_user)
                print(f'[Command send] {command_new_user}')

                # ---------- 2. fetch his user_id
                command_get_user_id = f"select user_id from boomq_user where email = '{user_email}'"
                cursor.execute(command_get_user_id)
                user_id = cursor.fetchone()[0]

                print(f'[Command send] {command_get_user_id}')
                print(f'[Command resp] user_id: {user_id}')

                # ---------- 3. include to team
                command_include_to_team = f"insert into team_member(id, user_id, team_id, invitation_status, permission_list, invite_url, expired_at, created_at, updated_at) values ((select max(id) from team_member bu ) + 1,{user_id},{user_team_number},'ACCEPTED','[\"RUN\", \"VIEW\", \"MANAGE_USERS\", \"EDIT\", \"ADMIN\", \"MANAGE_USERS_IN_ORG\"]',null,null,CURRENT_DATE,CURRENT_DATE)"
                cursor.execute(command_include_to_team)
                print(f'[Command send] {command_include_to_team}')

                # ---------- 4. update authority
                command_update_authority = f"insert into authority (authority_id, authority, user_id) values ((select max(authority_id) from authority) + 1, 'ROLE_USER', {user_id})"
                cursor.execute(command_update_authority)
                print(f'[Command send] {command_update_authority}')

                print(f'[INFO] End iter {i}')

    except Exception as e:
        print(f'[ERROR] Error occured:{e.__class__.__name__},{e}')

    finally:

        if connection:
            connection.close()
            print(f"[INFO] Conenction closed")

        if tunnel:
            tunnel.stop()
            print(f"[INFO] Tunnel closed")


if __name__ == "__main__":
    main()
