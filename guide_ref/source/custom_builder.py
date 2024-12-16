from sphinx.util import logging

logger = logging.getLogger(__name__)

def setup(app):
    app.connect('source-read', process_source)
    return {'version': '1.0', 'parallel_read_safe': True}

def process_source(app, docname, source):
    lines = source[0].split('\n')
    new_lines = []
    skip_section = False
    module_contents_found = False
    
    for line in lines:
        # if line.strip() == 'Submodules':
        #     skip_section = True
        if line.strip() == 'Module contents':
            module_contents_found = True
            skip_section = True
        elif skip_section and line.strip() and not line.startswith(' '):
            if not module_contents_found:
                skip_section = False
        
        if not skip_section and not module_contents_found:
            new_lines.append(line)
    
    source[0] = '\n'.join(new_lines)
    logger.info(f"Processed {docname}: Removed Submodules and entire Module contents sections")