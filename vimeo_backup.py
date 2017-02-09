import vimeo
import json
import requests
import re
import os


# edit these settings
v = vimeo.VimeoClient(
    token='token here',
    key='key here', 
    secret='secret here'
    )

def download_file(url, local_filename):
    print "Downloading "+url+" to "+local_filename
    #local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                #f.flush() commented by recommendation from J.F.Sebastian
    return local_filename

def get_biggest_vid(vidset):
    max = 0
    for file in vidset['files']:
        if file['size'] > max:
            max = file['size']
            url = file['link']
    print 'Biggest file '+str(max)
    if max == 0:
	return
    else:
    	return url


# Make and check the request to the server for the "/me" endpoint.
about_me = v.get('/me')
assert about_me.status_code == 200  # Make sure we got back a successful response.

# Now go get the video information and store it to all_data
videos_url = '/me/videos'
all_data = []
vids = v.get(videos_url).json()
total = vids['total']
while len(all_data) < total:
    print 'Total vids:'+str(len(all_data)) + ' of ' + str(total)
    all_data.extend(vids['data'])
    next = vids['paging']['next']
    if next == None:
        break
    print "Getting next... "+next
    vids = v.get(next).json()

# Now download the largest file associated with each video
# (we assume that is the best quality)
for vidset in all_data:
    title = vidset['name']
    uri = get_biggest_vid(vidset)
    if uri == None:
	print "No videos for some reason... skipping"
	continue
    type = vidset['files'][0]['type'].split('/')[1]
    id = vidset['link'].split('/')[-1]
    filename = re.sub(r'\W+', '', title.replace(' ', '_')) + '_' + str(id) + '.' + type
    #print uri
    if os.path.exists(filename):
        print "Already downloaded "+filename+" probably - skipping. Might want to delete it to force download though!"
        continue
    download_file(uri, filename)
