
function is_number(str) {
	var charcode = 0;
	
	for (var i=0;i<str.length;i++) {
		charcode = str.charCodeAt(i);
		if(!(charcode >= 48 && charcode <= 57)) {
			return false;
		}
	}
	return true;
}

