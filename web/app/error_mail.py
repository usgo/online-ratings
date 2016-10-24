'''
Copyright (c) 2012 Jason Feinstein, http://jwf.us/

Permission is hereby granted, free of charge, to any person obtaining a copy of 
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to 
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of 
the Software, and to permit persons to whom the Software is furnished to do so, 
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

'''
Edited from original Flask-ErrorMail extension
'''
import traceback
from flask import request, current_app
from flask_mail import Message

def email_exception(exception):
    '''Handles the exception message from Flask by sending an email to the
    recipients defined in config.ADMINS
    '''

    msg = Message("[AGA Online Ratings|Flask] Exception: %s" % exception.__class__.__name__,
                    recipients=current_app.config['ADMINS'])
    msg_contents = [
        'Traceback:',
        '='*80,
        traceback.format_exc(),
    ]
    msg_contents.append('\n')
    msg_contents.append('Request Information:')
    msg_contents.append('='*80)
    for k, v in sorted(request.environ.items()):
        msg_contents.append('%s: %s' % (k, v))

    msg.body = '\n'.join(msg_contents) + '\n'

    mail = current_app.extensions.get('mail')
    mail.send(msg)

