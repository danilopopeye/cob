from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from cob.dns.models import *
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

@login_required
def domain_list(request):
	paginator = Paginator(DomainSerial.objects.all(), 20)
	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1

	try:
		ds = paginator.page(page)
	except (EmptyPage, InvalidPage):
		ds = paginator.page(paginator.num_pages)
	return render_to_response('dns/domain_list.html', {
		'domainserials': ds,
		'total': paginator.count,
	})

@login_required
def domain_detail(request, domain_id):
	domain = get_object_or_404(Domain, pk=domain_id)
	serials = Serial.objects.filter(domain=domain)
	domainserial = DomainSerial.objects.get(domain=domain)
	records = Record.objects.filter(domain=domain)
	records = records.filter(out_date__gt = domainserial.serial.start_date)
	records = records.filter(since_date__lt = domainserial.serial.end_date)
	paginator = Paginator(records, 20)

	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1

	try:
		records = paginator.page(page)
	except (EmptyPage, InvalidPage):
		records = paginator.page(paginator.num_pages)

	return render_to_response('dns/domain_detail.html',
		{ 'domain': domain,
		  'serials': serials,
		  'records': records,
		})

@login_required
def domain_compare(request):
	if request.method == 'POST':
		post = request.POST
		domain = get_object_or_404(Domain, name=post['domain'])
		# it should return 2 serials
		serials = Serial.objects.filter(domain=domain, serial__in=[post['serial1'], post['serial2']]).order_by('start_date')
		new_records = Record.objects.filter(domain=domain,
			since_date__gt = serials[0].end_date)
		rm_records = Record.objects.filter(domain=domain,
			out_date__lt = serials[1].end_date)
	else:
		print "error"

	return render_to_response('dns/domain_compare.html', {
		'domain': domain,
		'serials': serials,
		'new_records': new_records,
		'rm_records': rm_records,
	})

@login_required
def domain_new(request):
	if request.method != 'POST':
		return render_to_response('dns/domain_new.html', {})
	# POST is left
	post = request.POST
	# TODO there should be a better way...
	domain = Domain()
	if post['name']: domain.name = post['name']
	if post['serial_pattern']: domain.serial_pattern = post['serial_pattern']
	if post['source']: domain.source = post['source']
	if post['contact']: domain.contact = post['contact']
	if post['refresh']: domain.contact = post['refresh']
	if post['retry']: domain.retry = post['retry']
	if post['expire']: domain.expire = post['expire']
	if post['ttl']: domain.ttl = post['ttl']
	domain.save()

	return render_to_response('dns/domain_new.html', {
		'method': 'post',
	})
