#!/usr/bin/env python3
"""CLI tool for generating decoy documents with embedded tracking links."""

import os
import re

import click
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT


def add_hyperlink(paragraph, url, text):
    """Add a hyperlink to a paragraph."""
    part = paragraph.part
    r_id = part.relate_to(url, RT.HYPERLINK, is_external=True)

    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)

    new_run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")

    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rPr.append(u)

    text_elem = OxmlElement("w:t")
    text_elem.text = text

    new_run.append(rPr)
    new_run.append(text_elem)
    hyperlink.append(new_run)

    paragraph._p.append(hyperlink)


def validate_url(url):
    """Validate that the URL uses http or https scheme."""
    if not re.match(r"^https?://", url, re.IGNORECASE):
        raise click.BadParameter(
            f"URL must start with http:// or https:// (got: {url})"
        )
    return url


def validate_output_path(output):
    """Validate the output path is safe."""
    # Resolve to absolute and check for path traversal
    abs_path = os.path.abspath(output)
    cwd = os.path.abspath(os.getcwd())

    if not abs_path.startswith(cwd):
        raise click.BadParameter(
            f"Output path must be within the current directory (resolved to: {abs_path})"
        )

    if not output.endswith(".docx"):
        raise click.BadParameter("Output file must have a .docx extension")

    return abs_path


def strip_metadata(doc):
    """Remove auto-generated metadata that reveals the tool used."""
    core = doc.core_properties
    core.author = "Internal"
    core.comments = ""
    core.category = ""
    core.keywords = ""
    core.subject = ""


@click.group()
def cli():
    """Decoy & Honeypot Assistant CLI"""
    pass


@cli.command()
@click.option("--output", "-o", default="decoy.docx", help="Output file path (.docx)")
@click.option("--url", "-u", "beacon_url", required=True, help="Beacon URL (http/https)")
def docx(output, beacon_url):
    """Generate a .docx with an embedded login-page link."""
    # Validate inputs
    beacon_url = validate_url(beacon_url)
    output = validate_output_path(output)

    try:
        doc = Document()
        p = doc.add_paragraph("Confidential \u2013 do not distribute. ")
        add_hyperlink(p, beacon_url, "Open portal login")
        strip_metadata(doc)
        doc.save(output)
        click.echo(f"Decoy written to {output}")
    except PermissionError:
        click.echo(f"Error: Permission denied writing to {output}", err=True)
        raise SystemExit(1)
    except FileNotFoundError:
        click.echo(f"Error: Directory does not exist for {output}", err=True)
        raise SystemExit(1)
    except OSError as e:
        click.echo(f"Error writing file: {e}", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
