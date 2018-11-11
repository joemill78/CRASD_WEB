from __future__ import division
from flask import Flask, render_template, request, redirect, url_for, flash, Markup, session
from database import DB
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, NumberRange, Optional, Length, IPAddress
#from wtforms_components import IntegerField
from password_manager import PW_MANAGER
app = Flask(__name__)
app.secret_key ='s3cr3t'


class ValidateMonDevice(FlaskForm):
    id = StringField("id", validators=[DataRequired(), Length(max=10)])
    ip = StringField("ip", validators=[DataRequired(), IPAddress()])
    name = StringField("name", validators=[DataRequired(), Length(max=30)])

class ValidateEditMonDevice(FlaskForm):
    ip = StringField("ip", validators=[DataRequired(), IPAddress()])
    name = StringField("name", validators=[DataRequired(), Length(max=30)])

class ValidateDeviceRecords(FlaskForm):
    ip = StringField("ip", validators=[DataRequired(), IPAddress()])
    address = StringField("address", validators=[DataRequired(), Length(max=30)])
    city = StringField("city", validators=[DataRequired(), Length(max=20)])
    state = StringField("state", validators=[DataRequired(), Length(max=3)])
    zip = StringField("zip", validators=[DataRequired(), Length(max=5)])
    country = StringField("country", validators=[DataRequired(), Length(max=20)])
    phone = StringField("phone", validators=[DataRequired(), Length(max=12)])
    download = StringField("download", validators=[DataRequired(), Length(max=4)])
    upload = StringField("upload", validators=[DataRequired(), Length(max=4)])


def mem_to_meg(value):
    return round(int(value) / 1024)


def split_line(line):
    return line.split()


def to_mbps(value):
    return value / 1000000


def mem_to_g(value):
    return round(int(value) / 1024 / 1024)


@app.route("/events", methods=['GET', 'POST'])
def events():
    if not session.get('logged_in'):
        return render_template('login.html')
    pg = DB()
    pg.connect()
    monitoring = pg.get_all_h_mon_events()
    reachability = pg.get_all_h_reach_events()
    output = pg.get_device_info()
    datums = pg.get_device_datums()
    monitored_devices = pg.get_monitored_devices()
    active_mon_events = pg.get_active_mon_events()
    active_reachability_events = pg.get_active_reachability_events()
    interface_status = pg.get_interface_status()
    available_mon_events = pg.get_available_mon_events()

    if request.method == 'POST':
        selected = request.form.getlist('monitored')
        event_list = []
        event_monitor = []
        for event in available_mon_events:
            for key, value in event.items():
                if key == 'name':
                    event_list.append(value)
                if key == 'monitor':
                    event_monitor.append(value)

        # print selected
        # print event_list
        # print event_monitor
        change = False
        for answer_form, db_data, event_list in zip(selected, event_monitor, event_list):
            if answer_form != db_data:
                # print "need to update: ", event_list
                pg.update_mon_event(event_list, answer_form)
                change = True

        if change:
            flash("{0} Monitoring Event Updated".format(event_list))
            return redirect(url_for('events'))

    return render_template('events.html', monitoring=monitoring, reachability=reachability,output=output,
                           datums=datums, mem_to_g=mem_to_g, split_line=split_line, to_mbps=to_mbps,
                           monitored_devices=monitored_devices, active_mon_events=active_mon_events,
                           active_reachability_events=active_reachability_events,
                           interface_status=interface_status, available_mon_events=available_mon_events)


@app.route("/")
@app.route("/home")
def dashboard():
    if not session.get('logged_in'):
        return render_template('login.html')

    pg = DB()
    pg.connect()
    # Get device Info
    output = pg.get_device_info()
    datums = pg.get_device_datums()
    monitored_devices = pg.get_monitored_devices()
    active_mon_events = pg.get_active_mon_events()
    active_reachability_events = pg.get_active_reachability_events()
    interface_status = pg.get_interface_status()

    pg.close()
    return render_template('home.html', output=output, datums=datums, mem_to_g=mem_to_g,
                           split_line=split_line, to_mbps=to_mbps, monitored_devices=monitored_devices,
                           active_mon_events=active_mon_events, active_reachability_events=active_reachability_events,
                           interface_status=interface_status)


@app.route("/device/edit", methods=['GET', 'POST'])
def edit_device_info():
    if not session.get('logged_in'):
        return render_template('login.html')
    pg = DB()
    pg.connect()
    output = pg.get_device_info()
    datums = pg.get_device_datums()

    device = {}
    form = ValidateDeviceRecords()
    if request.method == 'POST':
        if request.form['submit_button'] == 'Cancel':
            return redirect(url_for('dashboard'))
        elif request.form['submit_button'] == 'Save':
            items_updated = ""
            if form.validate_on_submit():
                if request.form.get('status') != output['status']:
                    device['status'] = request.form.get('status')
                    items_updated += ' Status '
                if form.ip.data != output['ip']:
                    device['ip_address'] = form.ip.data
                    items_updated += ' IP Address '
                if form.download.data.strip() != str(output['download_rate']):
                    device['download_rate'] = form.download.data
                    items_updated += ' Download Rate '
                if form.upload.data != str(output['upload_rate']):
                    device['upload_rate'] = form.upload.data
                    items_updated += ' Upload Rate '
                if form.address.data != output['address']:
                    device['address'] = form.address.data
                    items_updated += ' Address '
                if form.city.data != output['city']:
                    device['city'] = form.city.data
                    items_updated += ' City '
                if form.state.data != output['state']:
                    device['state'] = form.state.data
                    items_updated += ' State '
                if form.country.data != output['country']:
                    device['country'] = form.country.data
                    items_updated += ' Country '
                if form.zip.data != output['zip']:
                    device['zip'] = form.zip.data
                    items_updated += ' Zip Code '

                if device:
                    pg.update_device(device) # we send data to postgres here
                    flash("Device Info Updated: " + items_updated)
                else:
                    flash("Device Info: No Changes Detected")
                return redirect(url_for('dashboard'))
            return render_template('edit_device_info.html', output=output, datums=datums,
                                   split_line=split_line, to_mbps=to_mbps, mem_to_g=mem_to_g, form=form)
    else:
        return render_template('edit_device_info.html', output=output, datums=datums,
                               split_line=split_line, to_mbps=to_mbps, mem_to_g=mem_to_g, form=form)


@app.route("/device/add", methods=['GET', 'POST'])
def add_mon_device():
    if not session.get('logged_in'):
        return render_template('login.html')
    pg = DB()
    pg.connect()
    output = pg.get_device_info()
    datums = pg.get_device_datums()

    device = {}
    form = ValidateMonDevice()
    if request.method == 'POST':
        if request.form['submit_button'] == "Cancel":
            return redirect(url_for('dashboard'))
        elif request.form['submit_button'] == "Save":

            # print form.validate_on_submit()
            if form.validate_on_submit():

                if form.id.data:
                    device['target_device_id'] = form.id.data
                if form.ip.data:
                    device['target_ip_address'] = form.ip.data
                if form.name.data:
                    device['identifier'] = form.name.data
                if request.form.get('monitored'):
                    device['monitor'] = request.form.get('monitored')

                if device:
                    pg.insert_mon_device(device) # we send data to postgres here
                    flash("Monitored Device {0} Added".format(form.name.data))
                    return redirect(url_for('dashboard'))
            return render_template('add_monitored_device.html', output=output, datums=datums,
                                   split_line=split_line, to_mbps=to_mbps, mem_to_g=mem_to_g, form=form)

    else:
        return render_template('add_monitored_device.html', output=output, datums=datums,
                               split_line=split_line, to_mbps=to_mbps, mem_to_g=mem_to_g, form=form)


@app.route("/<device_id>/edit", methods=['GET', 'POST'])
def edit_mon_device(device_id):
    if not session.get('logged_in'):
        return render_template('login.html')
    pg = DB()
    pg.connect()
    output = pg.get_device_info()
    datums = pg.get_device_datums()
    monitored_device = pg.get_monitored_device(device_id)

    update = {}
    form = ValidateEditMonDevice()
    if request.method == 'POST':
        if request.form['submit_button'] == 'Cancel':
            return redirect(url_for('dashboard'))
        elif request.form['submit_button'] == 'Save':

            if form.validate_on_submit():
                if request.form.get('name') != monitored_device['name']:
                    update['identifier'] = request.form.get('name')
                    # print "need to update", request.form['name']
                if request.form.get('ip') != monitored_device['ip']:
                    update['target_ip_address'] = request.form.get('ip')
                    # print "need to update", request.form['ip']

                if request.form.get('monitored'):
                    monitor = request.form.get('monitored')
                    if monitor != monitored_device['monitor']:
                        update['monitor'] = request.form.get('monitored')
                        # print "need to update", request.form.get('monitored')

                if update:
                    pg.update_mon_device(update, device_id)
                    flash('Monitored Device {0} Updated'.format(device_id))
                else:
                    flash('Monitored Device: No Changes Detected')

                return redirect(url_for('dashboard'))

            return render_template('edit_monitored_devices.html', output=output, datums=datums,
                                    split_line=split_line, to_mbps=to_mbps, mem_to_g=mem_to_g,
                                    monitored_device=monitored_device, form=form)
    else:
        return render_template('edit_monitored_devices.html', output=output, datums=datums,
                               split_line=split_line, to_mbps=to_mbps, mem_to_g=mem_to_g,
                               monitored_device=monitored_device, form=form)


@app.route('/<device_id>/delete', methods=['GET', 'POST'])
def delete_mon_device(device_id):
    if not session.get('logged_in'):
        return render_template('login.html')
    pg = DB()
    pg.connect()
    output = pg.get_device_info()
    datums = pg.get_device_datums()
    monitored_device = pg.get_monitored_device(device_id)
    # print monitored_device

    if request.method == "POST":

        if request.form['submit_button'] == 'Cancel':
            return redirect(url_for('dashboard'))
        elif request.form['submit_button'] == 'Delete':
            pg.delete_mon_device(device_id)
            flash("Monitored Device: " + device_id + " Deleted")
            return redirect(url_for('dashboard'))
    else:
        return render_template('delete_mon_device.html', output=output, datums=datums,
                               split_line=split_line, to_mbps=to_mbps, mem_to_g=mem_to_g,
                               monitored_device=monitored_device)


@app.route('/charts', methods=['GET', 'POST'])
def charts():
    if not session.get('logged_in'):
        return render_template('login.html')
    pg = DB()
    pg.connect()
    output = pg.get_device_info()
    datums = pg.get_device_datums()
    data_memory = pg.get_mem_utilized()
    values = []
    labels = []
    for line in data_memory:
        values.append(mem_to_meg(line[0]))
        labels.append(line[1].strftime('%Y-%m-%d %H:%M:%S'))

    load_avg = pg.get_load_avg()
    values2 = []
    labels2 = []
    for line in load_avg:
        values2.append(line[0])
        labels2.append(line[1].strftime('%Y-%m-%d %H:%M:%S'))

    legend = 'Memory Used (Memory Available {0}) Megs'.format(mem_to_meg(datums['mem']))
    legend2 = "Load Average"

    return render_template('charts.html', output=output, datums=datums, mem_to_meg=mem_to_meg,
                           split_line=split_line, values=values, labels=labels, legend=legend,
                           values2=values2, labels2=labels2, legend2=legend2)


@app.route('/login', methods=['POST'])
def user_login():
    pm = PW_MANAGER()
    username = request.form['username'].encode('utf-8')
    password = request.form['password'].encode('utf-8')
    # print username, password
    if pm.validate(username, password):

        session['logged_in'] = True
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid username or password. Please try again!')
    return dashboard()


@app.route('/logout')
def logout():
    session['logged_in'] = False
    return dashboard()


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, threaded=True)
