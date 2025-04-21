#!/usr/bin/env python3
import click
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

def add_hyperlink(paragraph, url, text):
    """
    Add a hyperlink to a paragraph.
    """
    # Create the external relationship (rId) in the document
    part = paragraph.part
    r_id = part.relate_to(url, RT.HYPERLINK, is_external=True)

    # Build the <w:hyperlink> element and set its attribute
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)

    # Create a run (<w:r>) to hold the link text
    new_run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')

    # Underline style
    u = OxmlElement('w:u')
    u.set(qn('w:val'), 'single')
    rPr.append(u)

    # Text element
    text_elem = OxmlElement('w:t')
    text_elem.text = text

    # Assemble the run
    new_run.append(rPr)
    new_run.append(text_elem)
    hyperlink.append(new_run)

    # Append hyperlink to the paragraph’s XML
    paragraph._p.append(hyperlink)

@click.group()
def cli():
    """Decoy & Honeypot Assistant CLI"""
    pass

@cli.command()
@click.option('--output', '-o', default='decoy.docx', help='Output file path')
@click.option('--url', '-u', 'beacon_url', required=True, help='URL to embed in document')
def docx(output, beacon_url):
    """
    Generate a .docx with an embedded login-page link.
    """
    doc = Document()
    p = doc.add_paragraph("Confidential – do not distribute. ")
    add_hyperlink(p, beacon_url, "Open portal login")
    doc.save(output)
    click.echo(f"Decoy written to {output}")

if __name__ == '__main__':
    cli()
