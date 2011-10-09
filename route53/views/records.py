from boto.route53.exception import DNSServerError
from boto.route53.record import ResourceRecordSets
from flask import Blueprint, redirect, url_for, render_template, request, abort, flash

from route53.forms import RecordForm, RecordAliasForm, EditRecordForm, DeleteRecordAliasForm
from route53.connection import get_connection


def get_zone(zone_id, conn=None):
    if not conn:
        conn = get_connection()
    return conn.get_hosted_zone(zone_id)['GetHostedZoneResponse']['HostedZone']


records = Blueprint('records', __name__)


@records.route('/<zone_id>/alias/new', methods=['GET', 'POST'])
def new_alias(zone_id):
    conn = get_connection()
    zone = get_zone(zone_id, conn)
    error = None
    form = RecordAliasForm(request.values, csrf_enabled=False)

    if form.validate_on_submit():
        changes = ResourceRecordSets(conn, zone_id, form.comment.data)
        change = changes.add_change("CREATE", form.name.data, form.type.data,
            form.ttl.data)
        change.set_alias(form.alias_hosted_zone_id.data,
            form.alias_dns_name.data)
        changes.commit()
        flash('New alias %s for %s created!' % (form.type.data, form.name.data))
        return redirect(url_for('zones.detail', zone_id=zone_id))

    elbs = get_connection('elb').get_all_load_balancers()

    return render_template('records/new_alias.html', form=form, zone=zone,
        zone_id=zone_id, error=error, elbs=elbs)


@records.route('/<zone_id>/alias/update', methods=['GET', 'POST'])
def update_alias(zone_id):
    conn = get_connection()
    zone = get_zone(zone_id, conn)
    error = None
    form = RecordAliasForm(request.values, csrf_enabled=False)

    if form.validate_on_submit():

        changes = ResourceRecordSets(conn, zone_id, form.comment.data)

        change = changes.add_change("DELETE", form.name.data, form.type.data,
            form.ttl.data)
        change.set_alias(form.alias_hosted_zone_id.data,
            form.alias_dns_name.data)

        change = changes.add_change("CREATE", form.name.data, form.type.data,
            form.ttl.data)
        change.set_alias(form.alias_hosted_zone_id.data,
            form.alias_dns_name.data)

        changes.commit()
        flash('Updated alias %s for %s' % (form.type.data, form.name.data))
        return redirect(url_for('zones.detail', zone_id=zone_id))

    elbs = get_connection('elb').get_all_load_balancers()

    return render_template('records/update_alias.html', form=form, zone=zone,
        zone_id=zone_id, error=error, elbs=elbs)


@records.route('/<zone_id>/alias/delete', methods=['GET', 'POST'])
def delete_alias(zone_id):
    conn = get_connection()
    zone = get_zone(zone_id, conn)
    form = DeleteRecordAliasForm(request.values)

    if request.method == "GET":
        if form.values:
            abort(404)

    error = None
    if request.method == "POST":
        changes = ResourceRecordSets(conn, zone_id, '')
        change = changes.add_change("DELETE", form.name.data, form.type.data)
        change.set_alias(form.alias_hosted_zone_id.data,
            form.alias_dns_name.data)

        changes.commit()
        flash('Deleted alias %s' % form.name.data)
        return redirect(url_for('zones.detail', zone_id=zone_id))

    return render_template('records/delete_alias.html', zone=zone,
        zone_id=zone_id, error=error, form=form)


@records.route('/<zone_id>/new', methods=['GET', 'POST'])
def new(zone_id):
    conn = get_connection()
    zone = get_zone(zone_id, conn)
    form = RecordForm()
    error = None

    if form.validate_on_submit():
        changes = ResourceRecordSets(conn, zone_id, form.comment.data)
        change = changes.add_change("CREATE", form.name.data, form.type.data,
            form.ttl.data)
        for value in form.values:
            change.add_value(value)
        changes.commit()

        flash('Created new %s record %s' % (form.type.data, form.name.data))
        return redirect(url_for('zones.detail', zone_id=zone_id))

    return render_template('records/new.html', form=form, zone=zone,
        zone_id=zone_id, error=error)


@records.route('/<zone_id>/delete', methods=['GET', 'POST'])
def delete(zone_id):
    conn = get_connection()
    zone = get_zone(zone_id, conn)
    form = RecordForm(request.values)

    if request.method == "GET":
        if not form.values:
            abort(404)

    error = None
    if request.method == "POST":
        changes = ResourceRecordSets(conn, zone_id, form.comment.data)
        change = changes.add_change("DELETE", form.name.data, form.type.data, form.ttl.data)
        change.set_alias(None, None)
        [change.add_value(v) for v in form.values]
        changes.commit()

        flash('Deleted record %s' % form.name.data)
        return redirect(url_for('zones.detail', zone_id=zone_id))

    return render_template('records/delete.html', zone=zone, zone_id=zone_id,
        error=error, form=form)


@records.route('/<zone_id>/update', methods=['GET', 'POST'])
def update(zone_id):
    conn = get_connection()
    zone = get_zone(zone_id, conn)
    form = EditRecordForm(request.values)
    error = None

    if request.method == "GET" and not form.values:
        return redirect(url_for('.update_alias', zone_id=zone_id, **request.values.to_dict()))

    if request.method == "POST":
        changes = ResourceRecordSets(conn, zone_id, form.comment.data)
        del_change = changes.add_change("DELETE", form.previous_name.data,
            form.previous_type.data, form.previous_ttl.data)

        [del_change.add_value(v) for v in form.previous_values]

        change = changes.add_change("CREATE", form.name.data, form.type.data,
            form.ttl.data)

        [change.add_value(v) for v in form.values]

        changes.commit()
        flash('Updated %s record for %s' % (form.type.data, form.name.data))
        return redirect(url_for('zones.detail', zone_id=zone_id))

    return render_template('records/update.html', form=form, zone=zone,
        zone_id=zone_id, error=error)
