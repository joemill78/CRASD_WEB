import psycopg2
import collections


# This class is used for all interaction with postgres from the Crasd Web Interface
class DB(object):
    def __init__(self):
        self.db = 'cdb'
        self.user = 'crasd'
        self.conn = None
        self.host = '127.0.0.1'

    def connect(self):

        try:
            # print "connecting to PG database"
            self.conn = psycopg2.connect(host=self.host, database=self.db, user=self.user)

        except (Exception, psycopg2.DatabaseError) as error:
            print error

    def get_all_h_mon_events(self):
        try:
            cursor = self.conn.cursor()
            sql = ('select me.event_id, '
                           'et.name, '
                           'me.identifier, '
                           'me.start_time, '
                           'me.stop_time '
                   'from monitoring_event me '
                   'join event_type et on me.event_type_id = et.id '
                   'where me.stop_time is not null '
                   'and et.id in (1,2,3)')
            cursor.execute(sql)

            rows = cursor.fetchall()
            cursor.close()
            return rows

        except (Exception, psycopg2.DatabaseError) as error:
            print error

    def get_all_h_reach_events(self):
        try:
            cursor = self.conn.cursor()
            sql = ('select me.event_id, '
                           'ph.identifier, '
                           'ph.target_ip_address, '
                           'me.start_time, '
                           'me.stop_time '
                   'from monitoring_event me '
                   'join monitoring_ping_host ph on ph.target_ip_address = me.identifier '
                   'where me.event_type_id in (4) '
                   'and me.stop_time is not null')
            cursor.execute(sql)

            rows = cursor.fetchall()
            cursor.close()
            return rows

        except (Exception, psycopg2.DatabaseError) as error:
            print error

    def get_active_mon_events(self):
        try:
            cursor = self.conn.cursor()
            columns = ('event_id', 'name', 'identifier', 'start_time')
            sql = ('select me.event_id, '
                           'et.name, '
                           'me.identifier, '
                           'me.start_time '
                   'from monitoring_event me '
                   'join event_type et on me.event_type_id = et.id '
                   'where me.stop_time is null '
                   'and et.id in (1,2,3)')
            cursor.execute(sql)

            rows = cursor.fetchall()
            cursor.close()
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            return result

        except (Exception, psycopg2.DatabaseError) as error:
            print error

    def get_active_reachability_events(self):
        try:
            cursor = self.conn.cursor()
            columns = ('event_id', 'name', 'ip', 'start_time')
            sql = ('select me.event_id, '
                   'mph.identifier, '
                   'mph.target_ip_address, '
                   'me.start_time '
                   'from monitoring_event me '
                   'join monitoring_ping_host mph on me.identifier = mph.target_ip_address '
                   'and me.stop_time is null '
                   'and me.event_type_id = 4')
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            return result

        except (Exception, psycopg2.DatabaseError) as error:
            print error

    def get_interface_status(self):
        try:
            cursor = self.conn.cursor()

            sql = ('select dt.name, '
                   'dt.id, '
                   'md.value, '
                   'md.resource '
                   'from monitoring_datum md '
                   'join datum_type dt on dt.id = md.datum_type_id '
                   'and dt.id in (7,8,9,10)')
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            output = collections.defaultdict(dict)
            for row in rows:
                if row[1] == 7:
                    output[row[3]]['speed'] = row[2]
                if row[1] == 8:
                    output[row[3]]['duplex'] = row[2]
                if row[1] == 9:
                    output[row[3]]['auto'] = row[2]
                if row[1] == 10:
                    output[row[3]]['link'] = row[2]

            return output

        except (Exception, psycopg2.DatabaseError) as error:
            print error

    def close(self):
        self.conn.close()

    def get_device_info(self):
        try:
            cursor = self.conn.cursor()
            columns = ('device_id', 'name', 'brand', 'upload_rate',
                       'download_rate', 'address', 'state', 'city', 'country', 'zip', 'ip', 'phone', 'status')

            sql = ('select device_id, '
                           'name, '
                           'brand, '
                           'upload_rate, '
                           'download_rate, '
                           'address, '
                           'state, '
                           'city, '
                           'country, '
                           'zip, '
                           'ip_address, '
                           'phone, '
                           'status '
                   'from device')
            cursor.execute(sql)
            result = []
            rows = cursor.fetchall()
            cursor.close()
            for row in rows:
                result.append(dict(zip(columns, row)))
            output = result[0]
            return output

        except (Exception, psycopg2.DatabaseError) as error:
            print error

    def get_device_datums(self):
        try:
            cursor = self.conn.cursor()
            sql = ('select id, name, value, resource from monitoring_datum join datum_type on datum_type_id = id')
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            datums = {}
            for row in rows:
                if row[0] == 1:
                    datums['cpu_vendor'] = row[2]
                if row[0] == 2:
                    datums['cpu_model'] = row[2]
                if row[0] == 3:
                    datums['os'] = row[2]
                if row[0] == 5:
                    datums['kernel'] = row[2]
                if row[0] == 6:
                    datums['mem'] = row[2]
            return datums

        except (Exception, psycopg2.DatabaseError) as error:
            print error

    def get_monitored_devices(self):
        try:
            cursor = self.conn.cursor()
            sql = ('select target_device_id, identifier, target_ip_address, monitor from monitoring_ping_host')
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            columns = ('id', 'name', 'ip', 'monitor')
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))

            return result

        except (Exception, psycopg2.DatabaseError) as error:
            print error

    def get_monitored_device(self, device_id):
        try:
            cursor = self.conn.cursor()
            sql = ('select target_device_id, identifier, target_ip_address, monitor from monitoring_ping_host '
                   'where target_device_id = (%s)')
            cursor.execute(sql, (device_id,))
            row = cursor.fetchone()
            cursor.close()
            columns = ('id', 'name', 'ip', 'monitor')
            result = dict(zip(columns, row))

            return result

        except (Exception, psycopg2.DatabaseError) as error:
            print error

    def update_mon_device(self, data, device_id):
        update_sql = ""
        total = len(data)
        count = 1
        for key, value in data.items():
            update_sql += key + ' = ' + '\'' + value + '\''
            if count != total:
                update_sql += ', '
            count += 1

        sql = 'update monitoring_ping_host set {0} where target_device_id = {1}'.format(update_sql, device_id)
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            self.conn.commit()
            cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print error

    def update_device(self, data):
        update_sql = ""
        total = len(data)
        count = 1
        for key, value in data.items():
            if key == 'download_rate' or key == 'upload_rate':
                update_sql += key + ' = ' + value
            else:
                update_sql += key + ' = ' + '\'' + value + '\''
            if count != total:
                update_sql += ', '
            count += 1
        sql = 'update device set {0}'.format(update_sql)

        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            self.conn.commit()
            cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print error

    def delete_mon_device(self, device_id):
        try:
            cursor = self.conn.cursor()
            sql = 'delete from monitoring_ping_host where target_device_id = (%s)'
            cursor.execute(sql, (device_id,))
            self.conn.commit()
            cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print error

    def insert_mon_device(self, data):
        try:
            cursor = self.conn.cursor()
            sql = 'insert into monitoring_ping_host (device_id, target_ip_address, target_device_id, identifier, ' \
                  'event_type_id, monitor) values (125, %s, %s, %s, 4, %s)'
            cursor.execute(sql, (data['target_ip_address'], data['target_device_id'],
                                 data['identifier'], data['monitor']))
            self.conn.commit()
            cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print error

    def get_available_mon_events(self):
        try:
            cursor = self.conn.cursor()
            sql = ('select name, description, monitor from event_type order by id')
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            columns = ('name', 'description', 'monitor')
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))

            return result

        except (Exception, psycopg2.DatabaseError) as error:
            print error

    def update_mon_event(self, name, value):
        try:
            cursor = self.conn.cursor()
            sql = 'update event_type set monitor = (%s) where name = (%s)'
            cursor.execute(sql, (value, name))
            self.conn.commit()
            cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print error

    def get_mem_utilized(self):
        try:
            cursor = self.conn.cursor()
            sql = 'select value, time from memory_utilization order by time asc limit 20'
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except (Exception, psycopg2.DatabaseError) as error:
            print error

    def get_load_avg(self):
        try:
            cursor = self.conn.cursor()
            sql = 'select value, time from load_average order by time asc limit 20'
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except (Exception, psycopg2.DatabaseError) as error:
            print error

    def get_password(self, username):
        try:
            cursor = self.conn.cursor()
            sql = 'select password from users where username = (%s)'
            cursor.execute(sql, (username,))
            row = cursor.fetchone()
            cursor.close()
            return row
        except (Exception, psycopg2.DatabaseError) as error:
            print error

    def add_user(self, username, pwd):
        try:
            cursor = self.conn.cursor()
            sql = 'insert into users (username, password) values(%s, %s)'
            cursor.execute(sql, (username, pwd))
            self.conn.commit()
            cursor.close()

        except (Exception, psycopg2.DatabaseError) as error:
            print error


if __name__ == '__main__':
    pg = DB()
    pg.connect()

    out = pg.get_device_datums()
    if out:
        for r in out:
            print r[0][0]
    pg.close()
