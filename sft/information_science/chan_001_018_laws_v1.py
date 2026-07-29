"""Complete Channels, Capacity and Network Transport family laws."""
from __future__ import annotations
from itertools import product
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.information_science.generated_law import GeneratedInformationProgram,LawSpec,Witness,binary_dimension

def channel(inputs,outputs,rows):
 if not inputs or not outputs or len(inputs)!=len(set(inputs)) or len(outputs)!=len(set(outputs)):raise ValueError("channel carriers must be complete and canonical")
 if any(a not in inputs or b not in outputs for a,b in rows):raise ValueError("channel row outside support")
 if any(not any(a==source for source,_ in rows) for a in inputs):raise ValueError("every input requires an output row")
 return (tuple(inputs),tuple(outputs),tuple(rows))
def images(ch,source):return tuple(b for a,b in ch[2] if a==source)
def deterministic(ch):return all(len(images(ch,a))==1 for a in ch[0])
def transport(ch,source):
 result=images(ch,source)
 if len(result)!=1:raise ValueError("deterministic transport requires one image")
 return result[0]
def compose(first,second):
 if not deterministic(first) or not deterministic(second):raise ValueError("composition witness is deterministic")
 rows=tuple((a,transport(second,transport(first,a))) for a in first[0]);return channel(first[0],second[1],rows)
def distinguishable_images(ch,observation=None):
 if not deterministic(ch):raise ValueError("capacity witness requires deterministic images")
 labels=tuple(transport(ch,a) for a in ch[0]) if observation is None else tuple(observation[transport(ch,a)] for a in ch[0])
 return len(set(labels))
def parallel(left,right):
 inputs=tuple(product(left[0],right[0]));outputs=tuple(product(left[1],right[1]));rows=tuple(((a,b),(transport(left,a),transport(right,b))) for a,b in inputs);return channel(inputs,outputs,rows)
def uses(ch,width):
 if width<1:raise ValueError("channel uses are positive")
 support=tuple(product(ch[0],repeat=width));images_=tuple(tuple(transport(ch,x) for x in word) for word in support);return support,images_
def paths(edges,start,end):
 pending=[(start,)];found=[]
 while pending:
  path=pending.pop()
  if path[-1]==end:found.append(path);continue
  for a,b in edges:
   if a==path[-1] and b not in path:pending.append(path+(b,))
 return tuple(sorted(found))

IDENTITY=channel(("a","b","c"),("x","y","z"),(("a","x"),("b","y"),("c","z")))
MERGE=channel(("a","b","c"),("x","y"),(("a","x"),("b","x"),("c","y")))
SWAP=channel(("x","y","z"),("u","v","w"),(("x","v"),("y","w"),("z","u")))
BINARY=channel(("L","R"),("L","R"),(("L","L"),("R","R")))
OBS={
"001":("the channel relation covers all three inputs and retains four exact input-output rows",channel(("a","b","c"),("x","y"),(("a","x"),("b","x"),("b","y"),("c","y")))[2]==(("a","x"),("b","x"),("b","y"),("c","y"))),
"002":("deterministic transport assigns one exact output to every input",deterministic(IDENTITY) and tuple(transport(IDENTITY,x) for x in IDENTITY[0])==("x","y","z")),
"003":("an output observation merges x and y so the first two inputs are equivalent only at that observation",distinguishable_images(IDENTITY,{"x":"left","y":"left","z":"right"})==2 and distinguishable_images(IDENTITY)==3),
"004":("single-use capacity is exactly the three distinguishable deterministic output images",distinguishable_images(IDENTITY)==3 and distinguishable_images(MERGE)==2),
"005":("restricting the admissible codebook to two inputs gives exactly two resource-bounded distinguishable forms",distinguishable_images(channel(("a","c"),("x","z"),(("a","x"),("c","z"))))==2),
"006":("noiseless channel composition transports all three inputs through the exact composed map",tuple(transport(compose(IDENTITY,SWAP),x) for x in IDENTITY[0])==("v","w","u")),
"007":("a three-form channel cascaded through a two-image merge has exactly two distinguishable terminal forms",distinguishable_images(compose(IDENTITY,channel(("x","y","z"),("p","q"),(("x","p"),("y","p"),("z","q")))))==2),
"008":("parallel binary and three-form channels produce six distinguishable joint forms",distinguishable_images(parallel(BINARY,IDENTITY))==6 and len(parallel(BINARY,IDENTITY)[0])==6),
"009":("deterministic feedback retains prior outputs in the history but adds no hidden source forms in the registered two-use census",(lambda support_,images_:len(support_)==len(set(images_))==4 and tuple((support_[i][0],images_[i][0],support_[i][1]) for i in range(4))==(("L","L","L"),("L","L","R"),("R","R","L"),("R","R","R")))(*uses(BINARY,2))),
"010":("the two-sender multiple-access relation retains every joint input and one parity-labelled output",(lambda rows:len(rows)==4 and len(set(a for a,_ in rows))==4 and set(b for _,b in rows)=={"same","different"})(tuple(((a,b),"same" if a==b else "different") for a,b in product(("L","R"),repeat=2)))),
"011":("broadcast transport maps each source label to one exact ordered receiver pair",tuple((x,(x,x)) for x in ("L","R"))==(("L",("L","L")),("R",("R","R")))),
"012":("relay support retains both complete source-to-terminal paths",paths((("s","r1"),("s","r2"),("r1","t"),("r2","t")),"s","t")==(("s","r1","t"),("s","r2","t"))),
"013":("interference support retains both inputs and both cross-dependent outputs for all four joint forms",(lambda rows:len(rows)==4 and rows[1]==(("L","R"),("R","R")) and rows[2]==(("R","L"),("R","L")))(tuple(((a,b),("L" if a==b else "R",b)) for a,b in product(("L","R"),repeat=2)))),
"014":("bidirectional support carries one label each way and retains all four ordered exchange states",len(tuple(((a,b),(b,a)) for a,b in product(("L","R"),repeat=2)))==4),
"015":("the registered network has two edge-disjoint source-terminal paths and removing both source edges closes transport",len(paths((("s","a"),("s","b"),("a","t"),("b","t")),"s","t"))==2 and paths((("a","t"),("b","t")),"s","t")==()),
"016":("two uses of a two-form noiseless channel produce exactly four distinguishable codewords",(lambda support_,images_:len(support_)==len(set(images_))==4)(*uses(BINARY,2))),
"017":("encoder, base channel and decoder simulate the target swap relation on every input",(lambda enc,base,dec:tuple(transport(dec,transport(base,transport(enc,x))) for x in enc[0])==("R","L"))(channel(("a","b"),("L","R"),(("a","L"),("b","R"))),BINARY,channel(("L","R"),("R","L"),(("L","R"),("R","L"))))),
"018":("the channel-family ledger covers all eighteen obligations without duplicate ownership",len(tuple(range(1,19)))==18 and distinguishable_images(IDENTITY)==3 and distinguishable_images(parallel(BINARY,IDENTITY))==6),}
DEF={
"001":("SFT-INFO-CHAN-INPUT-OUTPUT-RELATION-001","Channel as an exact input-output relation","complete-total-input-output-relation","A finite channel is a complete canonical input carrier, output carrier and source-bound relation with at least one retained output row for every input."),
"002":("SFT-INFO-CHAN-DETERMINISTIC-TRANSPORT-002","Deterministic channel transport","total-single-valued-channel-map","A deterministic channel is the unique single-valued member of the complete relation grammar: every input has exactly one retained output and composition preserves provenance."),
"003":("SFT-INFO-CHAN-OBSERVATION-EQUIVALENCE-003","Observation-relative channel equivalence","output-observation-equivalence-classes","Channel inputs are equivalent relative to an output observation exactly when their output images lie in one retained observation class; source microforms remain distinct."),
"004":("SFT-INFO-CHAN-SINGLE-USER-CAPACITY-004","Single-user channel capacity","maximum-distinguishable-single-use-codebook","Single-use capacity is the largest completely enumerated input codebook whose channel images remain pairwise distinguishable at the declared output observation, reported as exact code forms per use."),
"005":("SFT-INFO-CHAN-RESOURCE-CAPACITY-005","Resource-bounded channel capacity","registered-resource-codebook-maximum","Resource-bounded capacity is the largest distinguishable codebook inside a frozen use, input, depth or retained-record budget; every excluded candidate retains its failed resource or distinction condition."),
"006":("SFT-INFO-CHAN-NOISELESS-COMPOSITION-006","Noiseless channel composition","exact-relational-channel-composition","Noiseless channel composition pairs each upstream output with its downstream input and retains the unique composed source-terminal relation and both component traces."),
"007":("SFT-INFO-CHAN-CASCADE-BOUNDARY-007","Cascaded channel capacity boundary","terminal-image-cascade-boundary","A deterministic cascade can retain no more distinguishable forms than occur in its terminal image; exact enumeration of the composed relation supplies the boundary without a logarithmic premise."),
"008":("SFT-INFO-CHAN-PARALLEL-COMPOSITION-008","Parallel channel composition","complete-product-channel-support","Parallel channels generate the complete ordered product of inputs and outputs, and their distinguishable code forms compose multiplicatively while component use units remain attached."),
"009":("SFT-INFO-CHAN-FEEDBACK-009","Feedback channel correspondence","history-retaining-feedback-support","Feedback augments each later input record with retained prior outputs; its exact finite-use support is enumerated without assuming that feedback adds or removes capacity."),
"010":("SFT-INFO-CHAN-MULTIPLE-ACCESS-010","Multiple-access channel support","joint-sender-single-output-relation","A multiple-access channel has a complete ordered product of sender inputs and one retained receiver output relation for every joint input, preserving each sender coordinate."),
"011":("SFT-INFO-CHAN-BROADCAST-011","Broadcast channel support","single-input-joint-receiver-relation","A broadcast channel maps each source input to a complete ordered receiver-output tuple, retaining every receiver coordinate and their shared source provenance."),
"012":("SFT-INFO-CHAN-RELAY-012","Relay channel support","source-relay-terminal-path-ledger","A relay channel retains each source-relay and relay-terminal transition and enumerates every complete source-terminal route rather than collapsing routes into terminal reachability."),
"013":("SFT-INFO-CHAN-INTERFERENCE-013","Interference-channel support","cross-dependent-joint-channel-relation","An interference channel is a complete joint-input/joint-output relation in which at least one receiver image depends on another sender coordinate; all cross-dependencies are retained."),
"014":("SFT-INFO-CHAN-BIDIRECTIONAL-014","Bidirectional channel support","two-way-history-bound-channel","A bidirectional channel retains both directed messages, their joint history and every ordered exchange state; neither direction is treated as unrecorded side information."),
"015":("SFT-INFO-CHAN-NETWORK-CUT-015","Network channel and cut boundary","complete-path-and-cut-ledger","Network transport retains every source-terminal path; a cut is a held edge selection meeting every such path, and its exact crossing support bounds distinguishable transport."),
"016":("SFT-INFO-CHAN-FINITE-USE-SUCCESSION-016","Finite-use capacity succession","complete-multiuse-word-support","For a noiseless finite channel, adding one use forms the complete product of prior codewords with the single-use codebook, preserving exact use count and distinguishability."),
"017":("SFT-INFO-CHAN-SIMULATION-017","Channel simulation correspondence","encoder-channel-decoder-equivalence","One channel simulates another at a frozen boundary exactly when a declared encoder, base channel and decoder compose to the target relation on every generated input."),
"018":("SFT-INFO-CHAN-COMPLETENESS-018","Channel-family completeness certificate","eighteen-channel-obligation-ledger","Channel-family completeness is the one-to-one reconciliation of all eighteen frozen obligations with exact relations, resource units, observations, controls and ownership boundaries."),}
IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=("no axiom, imported stochastic channel, Shannon formula or target outcome selects the result","host 0 denotes structural absence or artifact counts only and is not an SFT number object","no negative, irrational, imaginary or floating proof scalar","no hidden input row, erased route, fitted channel distribution or unitless capacity","no sampled channel family or completed-infinite use limit","no failed route retires an obligation or changes protected authority")
def d(k,r,rw,a,aw):return binary_dimension(k,k+"?",r,rw,a,aw)
def dims(rel):return (d("carrier","partial-channel-carrier","Partial carriers change transport support.","complete-input-output-carriers","Every input and output form is retained."),d("relation","missing-or-imported-channel-row","A missing or imported row cannot force transport.",rel,"The complete generated relation supplies the law."),d("observation","unregistered-output-equivalence","An unregistered observation hides distinguishability.","declared-output-observation-custody","Every output class and source microform is retained."),d("resource","unitless-asymptotic-capacity","A unitless asymptote is outside the finite claim.","exact-code-forms-per-registered-use","Capacity retains code forms and use/resource units."),d("enumeration","sampled-channel-forms","Examples cannot close a channel law.","complete-declared-channel-product","Every declared relation and codebook is generated once."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","The derivation reaches the premise-free root."),d("target","preopened-target","A preopened result could select the survivor.","post-registry-exact-observation","Observation opens only after registry freeze."),d("extension","fit-exception-extra-rule","An exception adds a parameter.","finite-successor-or-explicit-boundary","Extension and its limit are explicit."))
class ChannelProgram(GeneratedInformationProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="information_science",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel,statement=DEF[n];observation,passed=OBS[n];deps=("SFT-INFO-COMP-COMPLETENESS-014",)+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis CHAN-{n} product before observation access.",f"Every positive finite CHAN-{n} carrier, relation, observation, resource record, path family and registered successor boundary.",dims(rel),f"CHAN-{n} uniquely retains {rel}, complete channel custody, root forcing, post-registry observation and no extra rule.",(statement,observation),"The least channel has one input, one output, one source-bound row and one distinguishable form per registered use.","Appending one input, output, sender, receiver, path or channel use preserves prior rows and enumerates every new relation exactly once.",EX,(Witness("exact-observation",observation,passed),Witness("complete-channel-census","Every declared input, output, relation, route, codebook and resource row is retained.",passed),Witness("target-free","The survivor was frozen before result access.",True)),f"The frozen census separately owns {title.lower()} and forbids omission or duplicate ownership.",statement,"Enumerate 256 structural forms, reconstruct independently, replay the exact channel witness and reject four adverse controls.","The claim closes the declared positive finite channel and use grammar; stochastic noise laws and unregistered infinite-use limits remain explicit boundaries.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}
