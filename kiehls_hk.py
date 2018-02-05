#! /usr/bin/python
#-*- coding:UTF-8 -*-

from bs4 import BeautifulSoup
import urllib2
import re
import sys

def print_list(li):
    for item in li:
        print item

def get_categorylandinglink(soup):
    categorylandinglink = []
    for link in soup.find_all('li'):
        if 'class' in link.attrs:
            if 'categorylandinglink' in link['class']:
                href = link.find('a')['href']
                categorylandinglink.append(href)
    return categorylandinglink

def get_all_itemlist(categorylandinglink):
    item_herf_list = []
    for herf in categorylandinglink:
        soup = get_soup_from_herf(herf)
        for link in soup.find_all('a'):
            if 'class' in link.attrs:
                if 'product_name' in link['class']:
                    item_herf_list.append(link['href'])
    return item_herf_list

def get_item_image(soup):
    image_list = []
    for link in soup.find_all('img'):
        if 'class' in link.attrs:
            if 'product_image' in link['class']:
                image_list.append(link['src'])
    return image_list

def get_item_subtitle(soup):
    subtitle = None
    for link in soup.find_all('h2'):
        if 'class' in link.attrs:
            if 'product_subtitle' in link['class']:
                subtitle = link.string
                break
    return subtitle

def get_pdpDetailsList(soup):
    pdplist = []
    for link in soup.find_all('ul'):
        if 'class' in link.attrs:
            if 'pdpDetailsList' in link['class']:
                for item in link.find_all('li'):
                    pdplist.append(item.string)
    return pdplist

# Input: ['25','ml','75','ml']
def get_ml(str_list):
    result = ''
    for str in str_list:
        result += str
    return result

def get_item_description(soup):
    description = None
    for link in soup.find_all('div'):
        if 'class' in link.attrs:
            if 'product_detail_description' in link['class']:
                description_line = link.string
                if description_line is not None:
                    description = re.findall('\S+',link.string)
    if description is None:
        return description
    return get_ml(description)

def get_item_price(soup):
    price_list = []
    ml_list = []
    for link in soup.find_all('option'):
        if 'data-pricemoney' in link.attrs:
            price_list.append(link['data-pricemoney'])
            if link.string is not None:
                ml = get_ml(re.findall('\S+',link.string))
                ml_list.append(ml)
    return price_list,ml_list

def get_soup_from_herf(herf):
    response = urllib2.urlopen(herf)
    html = response.read()
    soup = BeautifulSoup(html, 'lxml')
    return soup

def get_item_title(soup):
    return soup.title.string

# title/subtitle/description == string
# subtitle/description could be None
# Others are List
def generate_md(title,description,subtitle,pdplist,image_src_list,price,ml):
    title_line = '## %s\n'%title

    if description is None:
        description_line = '\n'
    else:
        description_line = description+'\n'

    subtitle_line = '### %s\n'%subtitle
    pdplist_line = md_pdplist(pdplist)+'\n'
    image_src_line = '<img src="%s" width="200px" />\n\n'%image_src_list[0]
    price_line = md_price(price,ml)
    section = title_line+subtitle_line+price_line+'\n'+description_line+pdplist_line+'\n'+image_src_line+'\n'
    return section
    #fp = open('price.md','w')
    #fp.write(all)
    #fp.close()
    #pass

def md_pdplist(pdplist):
    pdplist_line = ''
    for item in pdplist:
        line = ' - %s\n'%item
        pdplist_line += line
    return pdplist_line

def md_price(price,ml):
    pm = dict(zip(price,ml))
    result = ''
    for item in pm:
        line = ''
        line = ' - %s\t\t%s\n'%(item,pm[item])
        result += line
    return result


def md_image(image_src_list):
    pass

def main():
    # response = urllib2.urlopen('http://www.kiehls.com.hk/en_HK/skincare-face')
    # response = urllib2.urlopen('http://www.kiehls.com.cn/skincare-face/')
    soup = get_soup_from_herf('http://www.kiehls.com.hk/zh_HK/search?cgid=skincare')

    categorylandinglink = get_categorylandinglink(soup)
    print_list(categorylandinglink)

    all_item_herf_list = get_all_itemlist(categorylandinglink)

    print '=== Item List ==='
    print_list(all_item_herf_list)

    all_section = ''

    for herf in all_item_herf_list:
        soup = get_soup_from_herf(herf)

        title = get_item_title(soup)
        description = get_item_description(soup)
        subtitle = get_item_subtitle(soup)
        pdplist = get_pdpDetailsList(soup)
        image_src_list = get_item_image(soup)
        price,ml = get_item_price(soup)

        section = generate_md(title, description, subtitle, pdplist, image_src_list, price, ml)
        all_section += section
        print section

if __name__ == '__main__':
    sys.exit(main())