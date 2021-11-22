from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from .models import Customer
from .serializers import *

import json
import requests

import pandas as pd
import os
import schedule
import time
from schedule import Scheduler
import threading

import datetime

import logging


@api_view(['GET'])
def customers_data(request):
    """
 List  datas, or create a new data.
 """
    def myfuc(e):
        return e[request.query_params.get('sortField')]

    def myFunc(e):
        return e['margin']

    def get_respond(response):
        respond = []
        data = json.loads(response.text)
        for item in data:
            tmplist = []
            for itr1 in item['markets'][0]['bookmakers']:
                for itr2 in item['markets'][0]['bookmakers']:
                    tmp = {}
                    tmp['odds 1'] = itr1['odds']['decimal'][0]
                    tmp['bookmaker 1'] = itr1['bookmaker']
                    tmp['odds 2'] = itr2['odds']['decimal'][1]
                    tmp['bookmaker 2'] = itr2['bookmaker']
                    tmp['Match'] = item['home'] + ' vs ' + item['away']
                    tmp['MatchStatus'] = item['matchStatus']
                    tmp['Market'] = item['markets'][0]['name']
                    tmp['Competition'] = item['competition']['name']
                    tmp['margin'] = 1.0 / tmp['odds 1'] + 1.0 / tmp['odds 2']
                    if tmp['margin'] >= 1:
                        continue
                    tmplist.append(tmp)
            tmplist.sort(key=myFunc)
            # print(tmplist)
            respond += tmplist
        return respond

    def run_continuously(self, interval=1):
        """Continuously run, while executing pending jobs at each elapsed
        time interval.
        @return cease_continuous_run: threading.Event which can be set to
        cease continuous run.
        Please note that it is *intended behavior that run_continuously()
        does not run missed jobs*. For example, if you've registered a job
        that should run every minute and you set a continuous run interval
        of one hour then your job won't be run 60 times at each interval but
        only once.
        """

        cease_continuous_run = threading.Event()

        class ScheduleThread(threading.Thread):

            @classmethod
            def run(cls):
                while not cease_continuous_run.is_set():
                    self.run_pending()
                    time.sleep(interval)

        continuous_thread = ScheduleThread()
        continuous_thread.setDaemon(True)
        continuous_thread.start()
        return cease_continuous_run

    def job():
        respond = []
        try:
            url = "https://tennis-odds.p.rapidapi.com/odds/live"

            headers = {
                'x-rapidapi-host': "tennis-odds.p.rapidapi.com",
                'x-rapidapi-key': "8b0c5b01a7mshc7d6514f944f7fbp1fa232jsn36477d4cf98a"
            }
            response = requests.request("GET", url, headers=headers)
            respond += get_respond(response)
        except:
            print('error')
        try:

            url = "https://tennis-odds.p.rapidapi.com/odds/prematch"

            querystring = {"page": "0", "size": "25"}

            headers = {
                'x-rapidapi-host': "tennis-odds.p.rapidapi.com",
                'x-rapidapi-key': "8b0c5b01a7mshc7d6514f944f7fbp1fa232jsn36477d4cf98a"
            }

            response = requests.request(
                "GET", url, headers=headers, params=querystring)
            respond += get_respond(response)
        except:
            print('error')
        try:
            df_json = pd.DataFrame(respond)
            settings.FILE_NAME = os.path.dirname(os.path.realpath(
                __file__)) + '/excel/' + 'DATAFILE' + str(datetime.datetime.now()).replace('.', '-').replace(':', '-') + '.xlsx'
            df_json.to_excel(settings.FILE_NAME)
        except:
            print('error')

    def start_scheduler():
        scheduler = Scheduler()
        scheduler.every(40).seconds.do(job)
        scheduler.run_continuously()

    if not settings.SCHEDULE:
        settings.SCHEDULE = True
        Scheduler.run_continuously = run_continuously
        start_scheduler()
        job()
        logger = logging.getLogger("mylogger")

        logger.info('ok' + settings.FILE_NAME + 'ok')

    if request.method == 'GET':
        # request.query_params
        df = pd.read_excel(settings.FILE_NAME)
        restext = []
        for idx in range(len(df)):
            if request.query_params.get('MatchStatus[]'):
                if not request.query_params.get('MatchStatus[]') == df['MatchStatus'][idx]:
                    continue
            dic = {}
            for key in list(df):

                dic[key] = df[key][idx]
            restext.append(dic)
        # try:
        if request.query_params.get('sortOrder') == "descend":
            restext.sort(reverse=True, key=myfuc)
        if request.query_params.get('sortOrder') == "ascend":
            restext.sort(reverse=False, key=myfuc)
        # except:
        logger = logging.getLogger("mylogger")
        logger.info(request.query_params.get('MatchStatus[]'))
        return Response({'data': restext})


@api_view(['GET', 'POST'])
def customers_list(request):
    """
 List  customers, or create a new customer.
 """
    if request.method == 'GET':
        data = []
        nextPage = 1
        previousPage = 1
        customers = Customer.objects.all()
        page = request.GET.get('page', 1)
        paginator = Paginator(customers, 5)
        try:
            data = paginator.page(page)
        except PageNotAnInteger:
            data = paginator.page(1)
        except EmptyPage:
            data = paginator.page(paginator.num_pages)

        serializer = CustomerSerializer(
            data, context={'request': request}, many=True)
        if data.has_next():
            nextPage = data.next_page_number()
        if data.has_previous():
            previousPage = data.previous_page_number()

        return Response({'data': serializer.data, 'count': paginator.count, 'numpages': paginator.num_pages, 'nextlink': '/api/customers/?page=' + str(nextPage), 'prevlink': '/api/customers/?page=' + str(previousPage)})

    elif request.method == 'POST':
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def customers_detail(request, pk):
    """
 Retrieve, update or delete a customer by id/pk.
 """
    try:
        customer = Customer.objects.get(pk=pk)
    except Customer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CustomerSerializer(customer, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CustomerSerializer(
            customer, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
