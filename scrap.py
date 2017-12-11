from lxml import html
import requests

page = requests.get('http://www.sis.itu.edu.tr/tr/ders_programlari/LSprogramlar/prg.php')
tree = html.fromstring(page.content)

#This will create a list of course_codes
course_codes = tree.xpath('//select[@name="bolum"]/option[not(@selected)]/text()')

print 'Course Codes: '
for course_code in course_codes:
    print course_code
    link = 'http://www.sis.itu.edu.tr/tr/ders_programlari/LSprogramlar/prg.php?fb=' + course_code
    page = requests.get(link.strip())
    tree = html.fromstring(page.content)
    tds = tree.xpath('//table[@class="dersprg"]/tr[@onmouseover]/td')
    courses = []
    while len(tds) > 14:
        pice = tds[:14]
        courses.append(pice)
        tds   = tds[14:]
    courses.append(tds)

    if len(courses[0]) == 0:
        continue

    sections = []
    for course in courses:
        course_sections = [{}]
        course_sections[0]['crn'] = course[0].text
        course_sections[0]['course_code'] = course[1].getchildren()[0].text
        course_sections[0]['title'] = course[2].text
        course_sections[0]['instructor'] = course[3].text
        course_sections[0]['capacity'] = course[8].text
        course_sections[0]['enrolled'] = course[9].text


        buildings = course[4].text_content()
        days = list(filter(None, course[5].text_content().split(' ')))
        hours = list(filter(None, course[6].text_content().split(' ')))


        if len(course[7].text_content().strip()) == 0:
            classes_content = "---"
        else:
            classes_content = course[7].text_content()

        classes = list(filter(None, classes_content.split(' ')))

        sections_count = len(buildings) / 3

        for x in xrange(0,sections_count):
            if x >= len(course_sections):
                course_sections.append(course_sections[x-1].copy())
            course_section = course_sections[x]
            course_section['building'] = buildings[(x * 3): ((x + 1) * 3)]
            course_section['day'] = days[x]
            course_section['hour'] = hours[x]
            course_section['class'] = classes[x]

        for section in course_sections:
            print section
