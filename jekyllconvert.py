#!/usr/bin/env python
"""A script to convert jekyll blogposts into Lektor files."""

import os
import argparse
import logging
import re
import warnings


class JekyllError(RuntimeError):
    pass


log = logging.getLogger(__name__)

jekyll_re = re.compile('(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})'
                       '-(?P<slug>[-_a-zA-Z0-9]+)\.(?P<ext>[a-zA-Z]+)$')
yaml_re = re.compile("""(?P<key>\S+)\s*:\s*['"]?(?P<value>[^\n]+?)['"]?\s*\n""")

def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert jekyll blog posts into Lektor pages.")
    parser.add_argument('src_dir', type=str, help="Directory containing jekyll posts.")
    parser.add_argument(
        '--output', '-o', type=str, default='./content/',
        help="Destination directory for the Lektor content")
    parser.add_argument(
        '--debug', '-d', default=False,
        action='store_true', help='Enable debugging output.')
    parser.add_argument(
        '--verbose', '-v', default=False,
        action='store_true', help='Provide additional output.')
    parser.add_argument(
        '--quiet', '-q', default=False,
        action='store_true', help='Suppress console output.')
    parser.add_argument(
        '--force', '-f', default=False,
        action='store_true', help='Overwrite existing files.')
    args = parser.parse_args()
    return args


def convert_jekyll_file(filename: str, dest: str, force: bool):
    """Load a jekyll file and convert to Lektor syntax.
    
    Parameters
    ==========
    filename
      Path to the jekyll file to load.
    dest
      Directory in which to save the new Lektor content.
    force : optional
      Overwrite 
    
    Raises
    ======
    JekyllError
      The file is not a valid jekyll file, either because the
      front-matter is incorrect or the filename is not valid.
    
    """
    log.debug("Attempting to read '%s'", filename)
    # Parse filename
    match = jekyll_re.match(os.path.basename(filename))
    if not match:
        log.info("Invalid filename %s", filename)
        raise(JekyllError("Invalid filename %s" % filename))
    metadata = match.groupdict()
    metadata['pub_date'] = "{}-{}-{}".format(metadata.pop('year'),
                                         metadata.pop('month'),
                                         metadata.pop('day'),)
    body = ''
    # Parse the front-matter in the file
    with open(filename) as f:
        INIT = 0
        META = 1
        BODY = 2
        section = 0
        # Extract all the info from the old jekyll format
        for l in f.readlines():
            if '---' in l:
                section += 1
            elif section == META:
                # Parse the line as Jekyll front-matter
                yaml_match = yaml_re.match(l)
                if not yaml_match:
                    msg = ("Invalid front-matter '%s' in file '%s'"
                           "" % (l, filename))
                    log.warning(msg)
                    raise JekyllError(msg)
                # Add front-matter to the dictionary
                key, value = yaml_match.groups()
                metadata[key] = value
            elif section == BODY:
                # Regular body content, so save for later
                body += l
            elif section >BODY:
                raise JekyllError("Unexpected error parsing '%s'" % filename)
        log.debug("Read metadata: %s", str(metadata))
        # Check if the lektor file currently exists
        new_dir = os.path.join(dest, metadata.pop('slug'))
        new_file = os.path.join(new_dir, 'contents.lr')
        if os.path.exists(new_file) and not force:
            log.warning("File '%s' already exists." % new_file)
            raise OSError("File '%s' already exists." % new_file)
        if os.path.exists(new_file) and force:
            log.info("Overwriting existing file '%s'." % new_file)
        # Create the directory if necessary
        if not os.path.exists(new_dir):
            log.debug("Creating directory '%s'", new_dir)
            os.makedirs(new_dir)
        # Create the new file
        log.debug("Writing to file '%s'", new_file)
        with open(new_file, mode='w') as f:
            # Write the model data
            for key, value in metadata.items():
                f.write("{key}: {value}".format(key=key, value=value))
                f.write("\n---\n")
            # Write the document body
            f.write("body:\n\n")
            f.write(body)


def process_jekyll_item(path: str, dest_dir: str, force: bool):
    """Take a filesystem name and convert to Lektor content.
    
    If ``path`` is a file, attempt to read meta-data and save it in
    ``dest_dir``. If ``path`` is a directory, recursively descend into
    the it and process the underlying items. Non-jekyll files will be
    skipped with a warning.
    
    Parameters
    ==========
    item
      Path to a jekyll file, or directory of jekyll files, to parse.
    dest_dir
      Path to a directory to hold the resulting Lektor content.
    force : optional
      If true, existing lektor files will be overwritten.
    
    """
    log.debug("Processing '%s'", path)
    if os.path.isdir(path):
        # Get the new path to store content
        new_dest = os.path.join(dest_dir, os.path.basename(path))
        log.debug("New destination: %s", new_dest)
        # Recursively parse the contents of the directory
        for file_ in os.listdir(path):
            new_path = os.path.join(path, file_)
            process_jekyll_item(new_path, new_dest, force=force)
    else:
        # Try and process as a jekyll file
        try:
            convert_jekyll_file(path, dest_dir, force=force)
        except JekyllError as r:
            msg = "Skipping invalid file: {}".format(path)
            log.warning(msg)
            warnings.warn(msg)


def main():
    # Process arguments
    args = parse_args()
    src_dir = args.src_dir
    dest_dir = args.output
    # Set up default logging
    if args.quiet:
        warnings.filterwarnings("ignore")
        logging.basicConfig(level=logging.CRITICAL)
    elif args.verbose:
        logging.basicConfig(level=logging.INFO)
    elif args.debug:
        logging.basicConfig(level=logging.DEBUG)
    # Launch the jekyll processing recursively
    process_jekyll_item(src_dir, dest_dir, force=args.force)

if __name__ == '__main__':
    main()
