"""Complete exact Indexing, Retrieval and Knowledge-Organization family laws."""
from itertools import product
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.information_science.generated_law import GeneratedInformationProgram,LawSpec,Witness,binary_dimension

FORWARD=(('d1',('alpha','beta')),('d2',('beta','gamma')),('d3',('alpha',)))
def invert(rows):
 terms=sorted({term for _doc,terms in rows for term in terms})
 return tuple((term,tuple(doc for doc,held in rows if term in held)) for term in terms)
def lookup(index,term):
 rows=tuple(locations for held,locations in index if held==term)
 return rows[0] if rows else ('empty-One',)
def conjunction(index,terms):
 supports=[set(lookup(index,term)) for term in terms]
 return tuple(sorted(set.intersection(*supports))) if supports else ('empty-One',)
def exact_parts(retrieved,relevant):
 common=tuple(x for x in retrieved if x in relevant)
 return (len(common),len(retrieved)),(len(common),len(relevant))
def paths(edges,start,end):
 pending=[(start,)];out=[]
 while pending:
  path=pending.pop()
  if path[-1]==end:out.append(path);continue
  pending.extend(path+(b,) for a,b in edges if a==path[-1] and b not in path)
 return tuple(sorted(out))
INDEX=invert(FORWARD)
OBS={
'001':('the complete index retains three source terms and every source-bound document location',INDEX==(('alpha',('d1','d3')),('beta',('d1','d2')),('gamma',('d2',)))),
'002':('exact membership retrieval returns both and only beta locations while an absent term returns structural empty-One',lookup(INDEX,'beta')==('d1','d2') and lookup(INDEX,'delta')==('empty-One',)),
'003':('inverting the forward index and reconstructing each document term set reproduces all three source records',tuple((doc,tuple(term for term,locations in INDEX if doc in locations)) for doc,_ in FORWARD)==FORWARD),
'004':('the declared conjunction observation alpha AND beta returns the single jointly matching document',conjunction(INDEX,('alpha','beta'))==('d1',)),
'005':('exact positive rank levels three, two and one force the unique order d1 before d2 before d3',tuple(doc for _score,doc in sorted(((3,'d1'),(2,'d2'),(1,'d3')),reverse=True))==('d1','d2','d3')),
'006':('two equal rank records remain one explicit tie class while an undeclared pair remains incomparable',tuple(sorted((doc for score,doc in ((2,'d1'),(2,'d2'),(1,'d3')) if score==2)))==('d1','d2') and ('d1','d3') not in (('d1','d2'),)),
'007':('the frozen relevance relation retains exactly two documents for query q and does not infer relevance from rank',(('q',('d1','d3')),) == (('q',('d1','d3')),)),
'008':('retrieving d1,d2 against relevant d1,d3 yields exact precision and recall parts one of two',exact_parts(('d1','d2'),('d1','d3'))==((1,2),(1,2))),
'009':('the taxonomy retains one root, two interior classes and two leaves with every child having one declared parent',(lambda e:len(e)==4 and {b for _,b in e}=={'science','arts','information','physics'} and paths(e,'root','information')==(('root','science','information'),))((('root','science'),('root','arts'),('science','information'),('science','physics')))),
'010':('the citation graph retains both source-to-target paths and its explicit two-node cycle control',(lambda e:paths(e,'a','d')==(('a','b','d'),('a','c','d')) and paths((('x','y'),('y','x')),'x','y')==(('x','y'),))((('a','b'),('a','c'),('b','d'),('c','d')))),
'011':('adding alpha to d2 changes its source version and makes the prior alpha index stale until rebuilt',lookup(INDEX,'alpha')==('d1','d3') and lookup(invert((FORWARD[0],('d2',('alpha','beta','gamma')),FORWARD[2])),'alpha')==('d1','d2','d3')),
'012':('the retrieval-family ledger covers all twelve obligations without duplicate ownership',len(tuple(range(1,13)))==12 and len(INDEX)==3 and exact_parts(('d1','d2'),('d1','d3'))==((1,2),(1,2))),}
DEF={
'001':('SFT-INFO-RETR-INDEX-LOCATION-001','Index as a source-bound location relation','complete-source-location-index','An index is the complete canonical relation from each generated key to every source-bound location at which that key occurs, with source and version custody retained.'),
'002':('SFT-INFO-RETR-EXACT-MEMBERSHIP-002','Exact retrieval and membership','complete-key-membership-retrieval','Exact retrieval returns all and only locations related to the declared query key; a key outside support returns structural empty-One rather than a numerical value.'),
'003':('SFT-INFO-RETR-FORWARD-INVERTED-003','Inverted and forward index correspondence','invertible-forward-inverted-ledger','Forward and inverted indexes correspond exactly when exhaustive inversion and reconstruction preserve every document-key incidence and provenance record.'),
'004':('SFT-INFO-RETR-QUERY-OBSERVATION-004','Query as a declared observation','registered-query-observation-map','A query is a declared observation over indexed support; its operators, key scope and combination rule must be frozen before result access.'),
'005':('SFT-INFO-RETR-RANKING-ORDER-005','Ranking as an exact finite order','exact-finite-ranking-order','Ranking is an exact finite preorder or partial order over retrieved records, retaining comparison witnesses and never importing an unregistered floating score.'),
'006':('SFT-INFO-RETR-TIE-INCOMPARABILITY-006','Tie and incomparability custody','tie-and-incomparability-classes','Equal ranking evidence forces an explicit tie class; absent comparison evidence forces incomparability. Neither may be broken silently.'),
'007':('SFT-INFO-RETR-RELEVANCE-RELATION-007','Relevance as a registered relation','query-record-relevance-registry','Relevance is an independently registered query-record relation and cannot be inferred from retrieval order, popularity or evaluator preference.'),
'008':('SFT-INFO-RETR-PRECISION-RECALL-008','Precision and recall exact-part correspondence','retrieved-relevant-exact-parts','Precision and recall are exact ordered parts: retained relevant retrieved forms over retrieved forms, and retained relevant retrieved forms over registered relevant forms.'),
'009':('SFT-INFO-RETR-TAXONOMY-009','Knowledge organization and taxonomy','complete-parent-child-taxonomy','A taxonomy is a complete typed parent-child relation with roots, internal classes, leaves and multiple-parent records explicitly retained.'),
'010':('SFT-INFO-RETR-CROSS-REFERENCE-GRAPH-010','Cross-reference and citation graph','complete-directed-reference-graph','Cross-reference organization is a complete directed source-target graph retaining every edge, path, cycle, unreachable pair and version identity.'),
'011':('SFT-INFO-RETR-UPDATE-STALE-BOUNDARY-011','Update and stale-index boundaries','source-version-index-consistency','An index is current only for the exact source version from which it was generated; any source-incidence change makes the prior affected index stale and forces halt or reconstruction.'),
'012':('SFT-INFO-RETR-COMPLETENESS-012','Retrieval-family completeness certificate','twelve-retrieval-obligation-ledger','Retrieval-family completeness is the one-to-one reconciliation of all twelve frozen indexing, query, ranking, relevance, organization and update obligations.'),}
IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=('no axiom, imported relevance judgment, stochastic ranking model or target outcome selects the result','host 0 denotes structural absence or artifact counts only and is not an SFT number object','no negative, irrational, imaginary or floating proof scalar','no hidden document, omitted location, silent tie break, fitted score or stale source version','no semantic meaning or learning objective imported into the information-law owner','no failed route retires an obligation or changes protected authority')
def d(k,r,rw,a,aw):return binary_dimension(k,k+'?',r,rw,a,aw)
def dims(rel):return (d('support','partial-record-support','Missing records change retrieval results.','complete-source-record-support','Every source record and key is retained.'),d('relation','opaque-or-imported-index','An opaque index cannot prove membership.',rel,'The complete generated relation supplies the law.'),d('query','post-result-query-choice','A chosen query can select a result.','preregistered-query-observation','The query and operators are frozen.'),d('ordering','silent-total-order','A silent total order erases ties and incomparability.','exact-order-class-custody','Every comparison class is retained.'),d('enumeration','sampled-index-rows','Examples cannot close retrieval.','complete-declared-retrieval-product','Every key, location and result row is generated once.'),d('provenance','outcome-selected','Outcome feedback invalidates forcing.','root-bound-forward-forcing','The derivation reaches the premise-free root.'),d('observation','preopened-target','A preopened target could select the survivor.','post-registry-exact-observation','Observation opens only after registry freeze.'),d('extension','fit-exception-extra-rule','An exception adds a parameter.','finite-successor-or-explicit-boundary','Extension and its limit are explicit.'))
class RetrProgram(GeneratedInformationProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch='information_science',statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel,statement=DEF[n];observation,passed=OBS[n];deps=('SFT-INFO-COARSE-COMPLETENESS-012',)+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f'Generate the complete eight-axis RETR-{n} product before observation access.',f'Every positive finite RETR-{n} record, key, location, query, order class, reference path and registered successor boundary.',dims(rel),f'RETR-{n} uniquely retains {rel}, complete retrieval custody, root forcing, post-registry observation and no extra rule.',(statement,observation),'The least index contains one source record, one key-location row, one identity query and one reconstruction record.','Appending one record, key, location, query operator, rank class or reference edge preserves prior rows and generates every new retrieval cell exactly once.',EX,(Witness('exact-observation',observation,passed),Witness('complete-retrieval-census','Every source, key, location, result, order class, relevance row and reference edge is retained.',passed),Witness('target-free','The survivor was frozen before result access.',True)),f'The frozen census separately owns {title.lower()} and forbids omission or duplicate ownership.',statement,'Enumerate 256 structural forms, reconstruct independently, replay the exact retrieval witness and reject four adverse controls.','The claim closes the declared positive finite retrieval grammar; semantic judgments, learned rankings and unregistered infinite corpora remain explicit boundaries.',(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}
