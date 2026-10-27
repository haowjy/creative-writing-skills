"""Deterministic Google subset for service integration, not fidelity evidence."""
from copy import deepcopy
from drive_sync.google import DocumentObservation,DOC
from drive_sync.conversion import utf16


class FakeGoogle:
    identity={'account':'fake-account','client':'fake-client'}
    def __init__(self):
        self.files={}
        self.bodies={}
        self.styles={}
        self.calls=[]
    def inventory(self,operation_id=None):
        return tuple(deepcopy(m) for m in self.files.values() if operation_id is None or m['appProperties']['operation']==operation_id)
    def metadata(self,file_id):
        return deepcopy(self.files[file_id])
    def capabilities(self):
        return {'importFormats':{'text/html':[DOC]},'exportFormats':{}}
    def create(self,name,mime,source_id,operation_id,parent=None,data=None,import_mime=None):
        assert data is None, 'This fake tests identity creation, not HTML import fidelity'
        file_id='id-'+str(len(self.files)+1)
        self.files[file_id]=dict(id=file_id,name=name,mimeType=mime,parents=[parent] if parent else ['drive-root'],version='1',
                                 appProperties={'source':source_id,'operation':operation_id})
        self.bodies[file_id]=''
        self.styles[file_id]=[]
        self.calls.append(('create',file_id))
    def observe_document(self,file_id):
        text=self.bodies[file_id]+'\n'
        content=[{'endIndex':1,'sectionBreak':{}}]
        offset=1
        for line in text.splitlines(keepends=True):
            end=offset+utf16(line)
            boundaries={offset,end}
            for a,b,style in self.styles[file_id]:
                boundaries.update(x for x in (a,b) if offset<x<end)
            points=sorted(boundaries)
            elements=[]
            raw=line.encode('utf-16-le')
            for a,b in zip(points,points[1:]):
                style={}
                for start,stop,value in self.styles[file_id]:
                    if start<=a and b<=stop:
                        style.update(value)
                value=raw[(a-offset)*2:(b-offset)*2].decode('utf-16-le')
                elements.append({'startIndex':a,'endIndex':b,'textRun':{'content':value,'textStyle':style}})
            content.append({'startIndex':offset,'endIndex':end,'paragraph':{'elements':elements}})
            offset=end
        doc={'revisionId':self.files[file_id]['version'],'tabs':[{'tabProperties':{'tabId':'tab'},'documentTab':{'body':{'content':content}}}]}
        return DocumentObservation(self.metadata(file_id),doc,())
    def update_document(self,observation,batch):
        file_id=observation.metadata['id']
        assert batch['writeControl']=={'requiredRevisionId':self.files[file_id]['version']}
        for request in batch['requests']:
            if 'deleteContentRange' in request:
                self.bodies[file_id]=''
                self.styles[file_id]=[]
            elif 'insertText' in request:
                insert = request['insertText']
                offset = (insert['location']['index'] - 1) * 2
                raw = self.bodies[file_id].encode('utf-16-le')
                self.bodies[file_id] = (raw[:offset] + insert['text'].encode('utf-16-le') + raw[offset:]).decode('utf-16-le')
            elif 'updateTextStyle' in request:
                value=request['updateTextStyle']
                if value['fields']=='*':
                    self.styles[file_id]=[]
                else:
                    self.styles[file_id].append((value['range']['startIndex'],value['range']['endIndex'],value['textStyle']))
        self.files[file_id]['version']=str(int(self.files[file_id]['version'])+1)
        self.calls.append(('update',file_id))
        return {'documentId': file_id, 'writeControl': {'requiredRevisionId': self.files[file_id]['version']}}
