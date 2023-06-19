from curses import savetty
from importlib.resources import path
from statistics import mean
from urllib.request import Request
from django.shortcuts import render 
from TDSProject.models import DB1
from TDSProject.models import Q
from TDSProject.models import operators
from TDSProject.models import finalqquery

from django.contrib import messages
import json
from django.http import HttpResponseRedirect
from . import views
import requests
from TDSProject.forms import Qforms
import psycopg2
import requests
import json
import pandas as pd
from pybliometrics.scopus import ScopusSearch, AbstractRetrieval
#from wos import woslite_client
#import woslite_client
#from woslite_client.rest import ApiException

from metapub import PubMedFetcher
from functools import reduce

from django.http import HttpResponse
from django.template import loader

def HomePage(request):
    showdata = operators.objects.all()
    showdataf = finalqquery.objects.all()
    template = loader.get_template('Home.html')
    context = {"data":showdata,"dataf":showdataf }
    #return render(request, 'Home.html', {"data":showdata})
    return HttpResponse(template.render(context, request))


def search(request):
    print(request)
    if 'Search' in request.POST:
        keyword=request.POST.get("Query")
        database = request.POST.get("Database")
        print(database)

        #print(keyword)
        if database == 'Pubmed':
            num_of_articles=2
            fetch = PubMedFetcher()
            # get the  PMID for articles with keyword
            pmids = fetch.pmids_for_query(keyword)#, retmax=num_of_articles)    
            # get  articles
            articles = {}
            titles = {}
            abstracts = {}
            authors = {}
            links={}
            print("No of records collected :")
            print(len(pmids))
            for pmid in pmids:
                articles[pmid] = fetch.article_by_pmid(pmid)
                titles[pmid] = fetch.article_by_pmid(pmid).title
                abstracts[pmid] = fetch.article_by_pmid(pmid).abstract
                authors[pmid] = fetch.article_by_pmid(pmid).authors
                links[pmid] = "https://pubmed.ncbi.nlm.nih.gov/"+pmid+"/"
                # print(pmid,titles[pmid],abstracts[pmid],authors[pmid],links[pmid])
                InsertData(pmid,titles[pmid],abstracts[pmid],authors[pmid],links[pmid])
            return HttpResponseRedirect('/ManualQuration')
        if database == 'Scopus':
            #print("Inside Scopus Code ")
            s = ScopusSearch(query = keyword, 
                 subscriber=False, refresh = False, start=5,)# kwds = "Intelligence")

            df = pd.DataFrame(s.results)
            print("The number of records fetched from Scopus are : ", len(df))    
            
            df_merged = pd.DataFrame()
            #print(len(df_merged))
            df_merged["ID"] = df.eid
            df_merged["Title"] = df.title
            df_merged["Abstract"] = df.description
            df_merged["Author"] = df.creator
            
            #df_merged.head()
            #print(df_merged["Title"][0])    
            for i in range(len(df)):
                scopusid = df_merged["ID"][i]
                scopusid = scopusid.split('-')[2]
                title = df_merged["Title"][i]
                abstract = " "
                author = df_merged["Author"][i]
                link = " "
                InsertData(scopusid,title,abstract,author,link)
            return HttpResponseRedirect('/ManualQuration')

    elif 'AND' in request.POST:
        keyword=request.POST.get("keyword")
        keyword = "(" + keyword + ")"
        InsertOperator(keyword,'AND')
        return HttpResponseRedirect('/')
    
    elif 'OR' in request.POST:
        keyword=request.POST.get("keyword")
        keyword = "(" + keyword + ")" 
        InsertOperator(keyword,'OR')
        return HttpResponseRedirect('/')
    
    
    elif 'Done' in request.POST:
        keyword=request.POST.get("keyword")
        keyword = "(" + keyword + ")" 
        InsertOperator(keyword, ' ')
        return HttpResponseRedirect('/')
    
    elif 'ANDf' in request.POST:
        keyword=request.POST.get("Query1")
        keyword = "(" + keyword + ")"
        InsertFinalOperator(keyword,'AND')
        return HttpResponseRedirect('/')
    
    elif 'ORf' in request.POST:
        keyword=request.POST.get("Query1")
        keyword = "(" + keyword + ")" 
        InsertFinalOperator(keyword,'OR')
        return HttpResponseRedirect('/')
    
    
    elif 'Donef' in request.POST:
        keyword=request.POST.get("Query1")
        keyword = "(" + keyword + ")" 
        InsertFinalOperator(keyword, ' ')
        return HttpResponseRedirect('/')
    
    
        
    elif 'Validate' in request.POST:
        return HttpResponseRedirect('/')
        
    elif 'reset' in request.POST:
        reset()
        return HttpResponseRedirect('/') 
        
    elif 'reseto' in request.POST:
        resetoperator()
        return HttpResponseRedirect('/')    
    
    elif 'resetfq' in request.POST:
        resetFinalQuery()
        return HttpResponseRedirect('/')    
    
    else:
        return render(request, 'Home.html')

def ManualQuration(request):
    if 'Relevant papers' in request.POST:
        #print("Inside if")
        showdata = Q.objects.filter(f1=True)
        #print("After showdata")
        #print(showdata)
        return render(request, 'Quratedpage.html', {"data":showdata})

    elif 'Reviewed papers' in request.POST:
        #print("Inside if")
        showdata = Q.objects.filter(f2=True)
        #print("After showdata")
        #print(showdata)
        return render(request, 'Quratedpage.html', {"data":showdata})

    elif 'Relevant & Reviewed' in request.POST:
        #print("Inside if")
        showdata = Q.objects.filter(f1=True, f2=True)
        #print("After showdata")
        #print(showdata)
        return render(request, 'Quratedpage.html', {"data":showdata})

    else:
        showdata = Q.objects.all()
        return render(request, 'ManualQuration.html', {"data":showdata})


def Saveflag(request, pmid, fvalue,f):
    #print("Inside save flag")
    #print(pmid, f1value)
    if fvalue == 'True':
        fvalue = False
    else:
        fvalue = True

    #print(fvalue)
    #saveflag = Q.objects.get(PmId = pmid)
    #print(saveflag)
    connection = psycopg2.connect(user="postgres",
                                    password="16april1999",
                                    host="127.0.0.1",
                                    port="5432",
                                    database="TDSProjectG2_5")
    cursor = connection.cursor()
    if f == 'f1':
        postgres_Update_query = """ Update "TDSProjectQ" SET "f1"=%s WHERE "PmId" = %s"""
    elif f == 'f2':
        postgres_Update_query = """ Update "TDSProjectQ" SET "f2"=%s WHERE "PmId" = %s"""
    

    record_to_insert = (fvalue,pmid)
    cursor.execute(postgres_Update_query, record_to_insert)

    connection.commit()
    count = cursor.rowcount
    cursor.close()
    connection.close()
    #print(count, "Record Updates successfully into Q table")
        
    showdata = Q.objects.all()
    # print(showdata)
    return HttpResponseRedirect('/ManualQuration')

    
def get_scopus_info(SCOPUS_ID):
    
    MY_API_KEY = 'ddddb324df60ce6a1b5e3381615e1ac4'
    url = ("http://api.elsevier.com/content/abstract/scopus_id/"+ SCOPUS_ID+ "?field=authors,title,publicationName,volume,issueIdentifier,"+ "prism:pageRange,coverDate,article-number,doi,citedby-count,prism:aggregationType")
    resp = requests.get(url,headers={'Accept':'application/json','X-ELS-APIKey': MY_API_KEY})
    results = json.loads(resp.text.encode('utf-8'))
    #print(url)
    #print(resp)
    #print(results)

    fstring = '{title}, {journal}, {volume}.\n'
    return fstring.format(title=results['abstracts-retrieval-response']['coredata']['dc:title'].encode('utf-8'),
                          journal=results['abstracts-retrieval-response']['coredata']['prism:publicationName'].encode('utf-8'),
                          volume=results['abstracts-retrieval-response']['coredata']['prism:volume'].encode('utf-8'),
                          date=results['abstracts-retrieval-response']['coredata']['prism:coverDate'].encode('utf-8'),
                          )


def InsertData(pmid,Title,Abstract,Author,Link):
    try:
        connection = psycopg2.connect(user="postgres",
                                    password="16april1999",
                                    host="127.0.0.1",
                                    port="5432",
                                    database="TDSProjectG2_5")
        cursor = connection.cursor()

        postgres_insert_query = """ INSERT INTO "TDSProjectQ" ("PmId","Title", "Abstract", "Author","Links","f1","f2") VALUES (%s,%s,%s,%s,%s,%s,%s)"""
        record_to_insert = (pmid,Title,Abstract,Author,Link,False,False)
        cursor.execute(postgres_insert_query, record_to_insert)

        connection.commit()
        count = cursor.rowcount
        # print(count, "Record inserted successfully into Q table")

    except (Exception, psycopg2.Error) as error:
        print("Failed to insert record into Q table", error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            # print("PostgreSQL connection is closed")


def InsertOperator(keyword,operator):
    try:
        connection = psycopg2.connect(user="postgres",
                                    password="16april1999",
                                    host="127.0.0.1",
                                    port="5432",
                                    database="TDSProjectG2_5")
        cursor = connection.cursor()
        
        postgres_insert_query = """ INSERT INTO "TDSProjectoperators" ("keyword","operators") VALUES (%s,%s)"""
        record_to_insert = (keyword, (operator,))
        
        cursor.execute(postgres_insert_query, record_to_insert)

        connection.commit()
        count = cursor.rowcount
        #print(count, "Record inserted successfully into Q table")

    except (Exception, psycopg2.Error) as error:
        print("Failed to insert record into Q table", error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            # print("PostgreSQL connection is closed")

def InsertFinalOperator(keyword,operator):
    try:
        connection = psycopg2.connect(user="postgres",
                                    password="16april1999",
                                    host="127.0.0.1",
                                    port="5432",
                                    database="TDSProjectG2_5")
        cursor = connection.cursor()
        
        postgres_insert_query = """ INSERT INTO "TDSProjectfinalqquery" ("keyword","operators") VALUES (%s,%s)"""
        record_to_insert = (keyword, (operator,))
        
        cursor.execute(postgres_insert_query, record_to_insert)

        connection.commit()
        count = cursor.rowcount
        #print(count, "Record inserted successfully into Q table")

    except (Exception, psycopg2.Error) as error:
        print("Failed to insert record into Q table", error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            # print("PostgreSQL connection is closed")

def reset():
    try:
        connection = psycopg2.connect(user="postgres",
                                    password="16april1999",
                                    host="127.0.0.1",
                                    port="5432",
                                    database="TDSProjectG2_5")
        cursor = connection.cursor()
        postgres_deleteQ_query = """ DELETE FROM "TDSProjectQ" """
        
        cursor.execute(postgres_deleteQ_query)

        connection.commit()
        count = cursor.rowcount
        #print(count, "Record inserted successfully into Q table")

    except (Exception, psycopg2.Error) as error:
        print("Failed to Delete records from operators table", error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            # print("PostgreSQL connection is closed")


def resetoperator():
    try:
        connection = psycopg2.connect(user="postgres",
                                    password="16april1999",
                                    host="127.0.0.1",
                                    port="5432",
                                    database="TDSProjectG2_5")
        cursor = connection.cursor()
        
        postgres_deleteO_query = """ DELETE FROM "TDSProjectoperators" """
        cursor.execute(postgres_deleteO_query)

        connection.commit()
        count = cursor.rowcount
        #print(count, "Record inserted successfully into Q table")

    except (Exception, psycopg2.Error) as error:
        print("Failed to Delete records from operators table", error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            # print("PostgreSQL connection is closed")


def resetFinalQuery():
    try:
        connection = psycopg2.connect(user="postgres",
                                    password="16april1999",
                                    host="127.0.0.1",
                                    port="5432",
                                    database="TDSProjectG2_5")
        cursor = connection.cursor()
        
        postgres_deleteO_query = """ DELETE FROM "TDSProjectfinalqquery" """
        cursor.execute(postgres_deleteO_query)

        connection.commit()
        count = cursor.rowcount
        #print(count, "Record inserted successfully into Q table")

    except (Exception, psycopg2.Error) as error:
        print("Failed to Delete records from operators table", error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            # print("PostgreSQL connection is closed")


