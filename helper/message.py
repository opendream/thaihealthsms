

def set_message(request, text, status='message'):
	if len(request.session.get('messages', [])) == 0:
		request.session['messages'] = []
	request.session['messages'].append({'text': text, 'class': status})