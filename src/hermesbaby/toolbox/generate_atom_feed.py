################################################################
#                                                              #
#  This file is part of HermesBaby                             #
#                       the software engineer's typewriter     #
#                                                              #
#      https://github.com/hermesbaby                           #
#                                                              #
#  Copyright (c) 2024 Alexander Mann-Wahrenberg (basejumpa)    #
#                                                              #
#  License(s)                                                  #
#                                                              #
#  - MIT for contents used as software                         #
#  - CC BY-SA-4.0 for contents used as method or otherwise     #
#                                                              #
################################################################

import os
import time
import argparse
from xml.etree.ElementTree import Element, SubElement, tostring
from datetime import datetime, timezone
import git

# Argument parser setup
parser = argparse.ArgumentParser(description="Generate Atom feed, RSS feed, and reStructuredText changelog for documentation changes.")
parser.add_argument(
    "--atom-feed-path",
    type=str,
    help="The full path where the docs_feed.atom file will be saved."
)
parser.add_argument(
    "--rss-feed-path",
    type=str,
    help="The full path where the docs_feed.rss file will be saved."
)
parser.add_argument(
    "--rst-file-path",
    type=str,
    help="The full path where the docs_changes.rst file will be saved."
)
args = parser.parse_args()

# Initialize Git Repo
repo = git.Repo(os.getcwd())

# Get the current commit and the previous commit
current_commit = repo.head.commit
previous_commit = repo.commit('HEAD^')

# Get the list of changed files in the 'docs/' directory
diff_files = repo.git.diff('--name-only', previous_commit, current_commit, '--', 'docs/').splitlines()

# Create Atom feed if --atom-feed-path is specified
if args.atom_feed_path:
    # Create the root element of the Atom feed
    feed = Element('feed', xmlns="http://www.w3.org/2005/Atom")

    # Add the title and link to the feed
    title = SubElement(feed, 'title')
    title.text = "Documentation Updates"

    link = SubElement(feed, 'link', href="http://example.com/your/docs/feed.atom")

    updated = SubElement(feed, 'updated')
    updated.text = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    # Add entries for each modified file
    for filepath in diff_files:
        entry = SubElement(feed, 'entry')
        entry_title = SubElement(entry, 'title')
        entry_title.text = f"Updated: {filepath}"

        entry_link = SubElement(entry, 'link', href=f"http://example.com/your/docs/{filepath}")

        entry_id = SubElement(entry, 'id')
        entry_id.text = f"urn:uuid:{os.urandom(16).hex()}"

        entry_updated = SubElement(entry, 'updated')
        entry_updated.text = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

        summary = SubElement(entry, 'summary')
        summary.text = f"File {filepath} was updated."

    # Convert the ElementTree to a byte string
    atom_feed = tostring(feed, 'utf-8')

    # Save the Atom feed to a file
    with open(args.atom_feed_path, 'wb') as f:
        f.write(atom_feed)

    print(f"Atom feed saved to {args.atom_feed_path}")

# Create RSS feed if --rss-feed-path is specified
if args.rss_feed_path:
    # Create the root element of the RSS feed
    rss = Element('rss', version="2.0")
    channel = SubElement(rss, 'channel')

    # Add the title, link, and description to the channel
    title = SubElement(channel, 'title')
    title.text = "Documentation Updates"

    link = SubElement(channel, 'link')
    link.text = "http://example.com/your/docs/feed.rss"

    description = SubElement(channel, 'description')
    description.text = "Latest updates to the documentation."

    pub_date = SubElement(channel, 'pubDate')
    pub_date.text = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z')

    # Add items for each modified file
    for filepath in diff_files:
        item = SubElement(channel, 'item')
        item_title = SubElement(item, 'title')
        item_title.text = f"Updated: {filepath}"

        item_link = SubElement(item, 'link')
        item_link.text = f"http://example.com/your/docs/{filepath}"

        item_guid = SubElement(item, 'guid')
        item_guid.text = f"http://example.com/your/docs/{filepath}"

        item_pub_date = SubElement(item, 'pubDate')
        item_pub_date.text = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z')

        item_description = SubElement(item, 'description')
        item_description.text = f"File {filepath} was updated."

    # Convert the ElementTree to a byte string
    rss_feed = tostring(rss, 'utf-8')

    # Save the RSS feed to a file
    with open(args.rss_feed_path, 'wb') as f:
        f.write(rss_feed)

    print(f"RSS feed saved to {args.rss_feed_path}")

# Create reStructuredText changelog if --rst-file-path is specified
if args.rst_file_path:
    # Define the title for the reStructuredText document
    rst_title = "Documentation Changes"

    # Create the underline based on the length of the title
    rst_underline = "#" * len(rst_title)

    # Initialize the reST content with the title and underline
    rst_content = [f"{rst_title}\n{rst_underline}\n"]

    # Add entries for each modified file
    for filepath in diff_files:
        rst_content.append(f"* **{filepath}** was updated.\n")

        # Optionally, include the diff for the file in reST format
        diff_text = repo.git.diff(previous_commit, current_commit, '--', filepath)
        rst_content.append(".. code-block:: diff\n")
        rst_content.append(f"\n{diff_text}\n")

    # Save the reStructuredText file
    with open(args.rst_file_path, 'w') as rst_file:
        rst_file.write("\n".join(rst_content))

    print(f"reStructuredText changelog saved to {args.rst_file_path}")
