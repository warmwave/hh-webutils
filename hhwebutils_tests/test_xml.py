# coding: utf-8
import unittest

from lxml import etree

from hhwebutils.xml import xml_to_string


class XmlToStringTestCase(unittest.TestCase):

    def setUp(self):
        self.ns = 'http://example.com/my_ns'
        self.ns_id = 'hha'
        self.ns_attrib = 'xmlns:{s.ns_id}="{s.ns}"'.format(s=self)

        self.content = '''
до текст
<tag1>content</tag1>
между текст
<tag2>содержание</tag2>
<tag3>
    <subtag>a</subtag>
    <subtag>b</subtag>

    <!-- comment -->

    <script type="text/javascript">
        var f = (function(a) {
          return function(b) {
                alert(a + b);
          };
        })(5);

        f(10);

        var str = '<div>' + '10' + 55 + '<div><h1>Hello</h1></div>' + '</div>';
        f(str);
    </script>

    <div class="foo">
        <a href="http://ru.ru" data-qa="test">Click me!</a>
    </div>
</tag3>
<tag4/>
после текст'''

        self.sample_xml_with_ns = '''\
<wrapper {s.ns_attrib}>
<{s.ns_id}:body>{s.content}
<{s.ns_id}:tagWithNs>abc</{s.ns_id}:tagWithNs></{s.ns_id}:body>
после body – этот текст нам не нужен
</wrapper>'''.format(s=self)

        self.sample_xml = '''\
<wrapper>
<body>{s.content}</body>
после body – этот текст нам не нужен
</wrapper>'''.format(s=self)

        self.sample_html_as_xml = '''\
<wrapper>
<body>
<div/>
<script>
    if (a &gt; b &amp;&amp; a &gt; 10) {{
        return a &lt; b + 5;
    }}
</script>
</body>
</wrapper>'''.format(s=self)

        self.result_html = u'''
<div></div>
<script>
    if (a > b && a > 10) {
        return a < b + 5;
    }
</script>'''

    def _get_ns_body(self):
        body = etree.fromstring(self.sample_xml_with_ns).find('{' + self.ns + '}body')
        self.assertTrue(body is not None)
        self.assertEqual(body.tag, '{' + self.ns + '}body')
        return body

    def test_with_ns(self):
        body = self._get_ns_body()
        real = xml_to_string(body)
        expected = u'''
до текст
<tag1 {s.ns_attrib}>content</tag1>
между текст
<tag2 {s.ns_attrib}>содержание</tag2>
<tag3 {s.ns_attrib}>
    <subtag>a</subtag>
    <subtag>b</subtag>

    <!-- comment -->

    <script type="text/javascript">
        var f = (function(a) {{
          return function(b) {{
                alert(a + b);
          }};
        }})(5);

        f(10);

        var str = '<div>' + '10' + 55 + '<div><h1>Hello</h1></div>' + '</div>';
        f(str);
    </script>

    <div class="foo">
        <a href="http://ru.ru" data-qa="test">Click me!</a>
    </div>
</tag3>
<tag4 {s.ns_attrib}/>
после текст
<{s.ns_id}:tagWithNs {s.ns_attrib}>abc</{s.ns_id}:tagWithNs>'''.format(s=self)
        self._assert_strings(real, expected)

    def test_clean_ns(self):
        body = self._get_ns_body()
        real = xml_to_string(body, clean_xmlns=True)
        self._assert_strings(real, self.content.decode('utf-8') + u'\n<tagWithNs>abc</tagWithNs>')

    def test_without_ns(self):
        body = etree.fromstring(self.sample_xml).find('body'.format(s=self))
        self.assertEqual(body.tag, 'body')
        real = xml_to_string(body)
        self._assert_strings(real, self.content.decode('utf-8'))
        self.assertEqual(xml_to_string(body, clean_xmlns=True), real)

    def test_html(self):
        body = etree.fromstring(self.sample_html_as_xml).find('body'.format(s=self))
        real = xml_to_string(body, clean_xmlns=True, method="html")
        self._assert_strings(real, self.result_html)

    def _assert_strings(self, real, expected):
        if real != expected:
            line = 0
            pos = 0
            for rchar, echar in zip(real, expected):
                pos += 1
                if rchar != echar:
                    self.fail(u'String not equals. Diff at postion {pos} on line {line}: "{rchar}" != "{echar}".\n\n'
                              u'Real: {real}.\n\nExpected: {expected}'.format(**locals()))
                if rchar == '\n':
                    line += 1
                    pos = 0
