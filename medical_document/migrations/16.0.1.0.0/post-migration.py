import html
import re

from lxml import etree
from openupgradelib import openupgrade

_PY_VAR_PATTERN = "[a-zA-Z_][a-zA-Z0-9_]*"

MAIL_TEMPLATE_MAKO_CHAR_FIELDS = [
    "email_from",
    "email_to",
    "email_cc",
    "reply_to",
    "partner_to",
    "lang",
    "scheduled_date",
]


def _migrate_placeholder_char(string):
    """
    Replace dynamic placeholders in char/text fields:
    Example: "Dear ${object.name}," -> "Dear {{object.name}},"
    """
    if not string:
        return string
    string = re.sub(r"\s?\|\s?safe\s?", "", string)
    pattern = r"\$\{([^}]*)\}"
    repl = r"{{\1}}"
    return re.sub(pattern, repl, string)


def repl_placeholder(match):
    """Aux. method. We declare it globally so we don't have scope issues from shell"""
    (expression,) = match.groups()
    expression = html.escape(expression)
    return f'<t t-out="{expression}"></t>'


def _migrate_placeholder_html(string):
    """
    Replace dynamic placeholders in HTML fields:
    Example: 'Your name is ${object.name}' -> 'Your name is <t t-out="object.name"></t>'
    Example:'${object.html_content | safe}' -> '<t t-out="object.html_content"></t>'
    """
    string = re.sub(r"\|\s*safe\s*(?=\W|$)", "", string)
    pattern = r"\$\{([^}]*)\}"
    string = re.sub(pattern, repl_placeholder, string)
    return string


def _migrate_end(string):
    """
    Replace mako block endings
    Example: '% endfor' -> '</t>'
    """
    pattern = r"%\s?end(if|for)\s*$"
    repl = r"</t>"
    return re.sub(pattern, repl, string, flags=re.MULTILINE)


def _migrate_else(string):
    """
    Replace mako elses (we close the previous block as well)
    Example: '% else' -> '</t>\n<t t-else="">'
    """
    pattern = r"%\s?else\s?:*$"
    repl = r'</t>\n<t t-else="">'
    return re.sub(pattern, repl, string, flags=re.MULTILINE)


def repl_if(match):
    """Aux. method. We declare it globally so we don't have scope issues from shell"""
    (if_expression,) = match.groups()
    if_expression = html.escape(if_expression)
    return f'<t t-if="{if_expression}">'


def _migrate_if(string):
    """
    Replace mako if blocks
    Example: '% if object.value == 1' -> '<t t-if="{{object.value == 1}}">'
    """
    pattern = r"%\s?if\s(.+)\s?:"
    return re.sub(pattern, repl_if, string, flags=re.MULTILINE)


def repl_for(match):
    """Aux. method. We declare it globally so we don't have scope issues from shell"""
    var_name, loop_expression = match.groups()
    loop_expression = html.escape(loop_expression)
    return f'<t t-foreach="{loop_expression}" t-as="{var_name}">'


def _migrate_for(string):
    """
    Replace mako for blocks
    Example: '% for line in lines' -> '<t t-foreach="lines" t-as="line">'
    """
    pattern = rf"%\s?for\s+({_PY_VAR_PATTERN})\s+in\s+(.+?)\s?:\s*$"  # noqa: E231
    return re.sub(pattern, repl_for, string, flags=re.MULTILINE)


def repl_set(match):
    """Aux. method. We declare it globally so we don't have scope issues from shell"""
    var_name, var_value = match.groups()
    var_value = html.escape(var_value)
    return f'<t t-set="{var_name}" t-value="{var_value}"/>'


def _migrate_set(string):
    """
    Replace mako variable assignments
    Example: '% set val = object.val -> '<t t-set="val" t-value="{{object.val}}">'
    """
    pattern = rf"%\s?set\s+({_PY_VAR_PATTERN})\s+=\s+(.+?)\s?:*$"  # noqa: E231
    return re.sub(pattern, repl_set, string, flags=re.MULTILINE)


def _migrate_html_attributes(string):
    """
    Parse attributes that might contain placeholder expressions.
    Example: '<a href="${object.name}'"> -> '<a t-attf-href="{{object.name}}">'
    """
    parser = etree.HTMLParser()
    root = etree.fromstring(string, parser)
    for element in root.iter():
        new_attrs = {}
        for attr_name, attr_value in element.attrib.items():
            new_attr_value = _migrate_placeholder_char(attr_value)
            if new_attr_value != attr_value:
                new_attrs[f"t-attf-{attr_name}"] = new_attr_value
            else:
                new_attrs[attr_name] = attr_value
        for attr in list(element.attrib.keys()):
            del element.attrib[attr]
        for attr_name, attr_value in new_attrs.items():
            element.set(attr_name, attr_value)
    return etree.tostring(root, pretty_print=True, encoding="unicode")


def mako_html_to_qweb(string):
    """Exlusive for the body content"""
    if not string:
        return string
    string = _migrate_html_attributes(string)
    string = _migrate_placeholder_html(string)
    string = _migrate_if(string)
    string = _migrate_for(string)
    string = _migrate_else(string)
    string = _migrate_end(string)
    string = _migrate_set(string)
    return string


@openupgrade.migrate()
def migrate(env, version):
    for tmpl in env["medical.document.type.lang"].search([]):
        tmpl.text = mako_html_to_qweb(tmpl.text)
    for tmpl in env["medical.document.template.lang"].search([]):
        tmpl.text = mako_html_to_qweb(tmpl.text)
