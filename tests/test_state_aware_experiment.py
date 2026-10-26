"""Synthetic runner contracts only: no actual gold, model, retrieval or run lock."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from contextlib import contextmanager
from types import SimpleNamespace

import pytest

from experiments.temporal_state_retrieval import state_aware_experiment as e
from experiments.temporal_state_retrieval import scoring


def encoded(value):
    return (json.dumps(value, indent=2) + "\n").encode()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value if isinstance(value, bytes) else encoded(value))


class FakeGit:
    def __init__(self, root):
        self.root = root
        self.parent = e.IMPLEMENTATION_PARENT
        self.implementation = "a" * 40
        self.head = "b" * 40
        self.is_ancestor = True
        self.changes = "A\t" + e.LOCK_PATH
        self.trusted = {}
        self.committed = {}
        self.lock_bytes = b""

    def call(self, *args):
        if args == ("rev-parse", "HEAD"): return self.head
        if args == ("branch", "--show-current"): return "temporal-state-retrieval-state-aware-v1"
        if args[0:2] == ("diff", "--name-status"): return self.changes
        if args[0] == "diff": return ""
        raise AssertionError(args)

    def blob(self, commit, path):
        if commit == self.parent and path == e.CANDIDATE_PATH: return encoded(self.trusted)
        if commit == self.head and path == e.LOCK_PATH: return self.lock_bytes
        return self.committed[path]

    def ancestor(self, *args): return self.is_ancestor
    def ignored(self, path): return Path(path).is_relative_to(self.root / "private_data")


@pytest.fixture
def formal_fixture(tmp_path):
    root = tmp_path / "synthetic_repository"
    root.mkdir()
    git = FakeGit(root)
    run_id = "phase_3b_state_aware_v1_run_20000101"
    output = root / "private_data/temporal_state_retrieval_experiment/phase_3b" / run_id
    bindings = {name: "private_data/temporal_state_retrieval_experiment/"+name+".json"
                for name in (*e.PRIVATE_LABELS, "baseline_trace")}
    inventory, metadata = [], []
    for prefix, source_root, count, project in (("EF", e.SOURCE_ROOTS[0], 4, "sample_echo_field"),
            ("RS", e.SOURCE_ROOTS[1], 7, "synthetic_archive"), ("SY", e.SOURCE_ROOTS[2], 7, "synthetic_loom")):
        for number in range(1, count+1):
            rid = f"{prefix}-R{number:02}"
            p = source_root+f"/process/{number}.md"
            save(root/p, b"Entirely synthetic fixture content.")
            inventory.append(dict(record_id=rid, project_id=project, path=p, sha256=e.digest(root/p), source_category="process"))
            metadata.append(dict(record_id=rid, project_id=project, source_category="process", record_state="undated_record"))
    public_manifest = "tests/fixtures/temporal_state_metadata/freeze_manifest.json"
    save(root/public_manifest, {"public_source_inventory": [r for r in inventory if not r["record_id"].startswith("RS")]})
    for name, prefix in (("echo_field", "EF"), ("signal_loom", "SY")):
        save(root/f"tests/fixtures/temporal_state_metadata/{name}.metadata.json", {"records": [r for r in metadata if r["record_id"].startswith(prefix)]})
    save(root/bindings["record_metadata"], {"records": [r for r in metadata if r["record_id"].startswith("RS")]})
    save(root/bindings["metadata_manifest"], {"protected_private_inputs": [{k:r[k] for k in ("path","sha256")} for r in inventory if r["record_id"].startswith("RS")]})
    for label in ("phase_1_gold", "phase_1_manifest", "baseline_trace"):
        save(root/bindings[label], b"Opaque synthetic bytes; not readable gold JSON.")
    model = tmp_path / "model_cache" / "synthetic-revision"
    save(model/"modules.json", b"[]"); save(model/"model.safetensors", b"synthetic weights, never loaded")
    baseline_manifest = "outputs/test_results/temporal_state_retrieval_baseline/run_manifest.json"
    save(root/baseline_manifest, {"private_raw_trace_sha256": e.digest(root/bindings["baseline_trace"]),
        "model_snapshot_files": {n:e.digest(model/n) for n in ("modules.json", "model.safetensors")},
        "device":"fake", "logical_cpu_count":1, "torch_threads":1})
    paths = set(e.REQUIRED_PUBLIC_PATHS) | {
        "project_knowledge/process/experiments/temporal_state_retrieval/phase_3b_implementation_review.md"}
    for p in paths:
        if not (root/p).exists(): save(root/p, b"synthetic committed artifact")
    save(root/e.RUNNER_TEST_PATH, b"synthetic test artifact")
    criteria = {"all_required_roles_minimum":[10,15], "hit_at_3_minimum":[10,15], "pair_coverage_at_2_minimum":[2,3],
        "closure_at_2_minimum":[2,3], "known_false_current_maximum":[1,9], "production_warm_median_limit_ms":44.028899996192195}
    common = {"protocol_sha256":e.digest(root/"project_knowledge/process/experiments/temporal_state_retrieval/phase_3_preregistration.md"),
        "intended_case_counts":{"production":18,"diagnostic":16},
        "intended_views":{k:{"documents":v[0],"chunks":v[1]} for k,v in e.VIEW_SIZES.items()},
        "intended_embedding_model":"all-MiniLM-L6-v2", "intended_model_snapshot_revision":model.name,
        "phase_1_original_benchmark_criteria":{"synthetic":"separate legacy criteria"},
        "phase_3_candidate_improvement_criteria":criteria}
    commitments={n:e.digest(root/p) for n,p in bindings.items()}
    git.trusted = dict(common, dependencies={}, public_artifacts=[{"path":p,"sha256":e.digest(root/p)} for p in sorted(paths)],
                       private_commitments={k:v for k,v in commitments.items() if k != "baseline_trace"})
    private = {"run_id":run_id,"implementation_commit":git.implementation,"inputs":bindings,
               "record_inventory":inventory,"output_root":output.relative_to(root).as_posix(),"model_snapshot":str(model)}
    private_path=output/"private_pre_run_lock.json"
    save(private_path,private)
    lock = dict(common, status="execution_authorised", execution_authorised=True, candidate_evaluation_run=False,
        run_count_allowed=1, experiment_version=e.EXPERIMENT_VERSION, implementation_commit=git.implementation,
        public_artifacts=[{"path":p,"sha256":e.digest(root/p)} for p in sorted(paths|{e.RUNNER_TEST_PATH})],
        private_commitments=commitments, private_lock_sha256=e.digest(private_path), python=sys.version.split()[0],
        dependencies={}, outputs={n:e.PUBLIC_DIRECTORY+"/"+n for n in e.PUBLIC_OUTPUTS},
        score_tolerance={"absolute":0,"relative":0},run_id=run_id,authorised_by="Synthetic reviewer",authorisation_date="2000-01-01")
    git.committed={p:(root/p).read_bytes() for p in paths|{e.RUNNER_TEST_PATH}}
    def sync():
        save(root/e.LOCK_PATH,lock);git.lock_bytes=(root/e.LOCK_PATH).read_bytes()
    sync()
    return dict(root=root,git=git,lock=lock,private=private,private_path=private_path,output=output,sync=sync)


def checked(f):
    return e.preflight(f["root"],f["root"]/e.LOCK_PATH,f["private_path"],git=f["git"])


def test_readonly_preflight_hashes_opaque_gold_and_checks_later_lock_commit(formal_fixture):
    f=formal_fixture
    before={p:p.read_bytes() for p in f["root"].rglob("*") if p.is_file()}
    context=checked(f)
    assert context["lock_commit"]!=context["lock"]["implementation_commit"]
    assert not (f["output"]/"execution_state.json").exists()
    assert before=={p:p.read_bytes() for p in f["root"].rglob("*") if p.is_file()}


@pytest.mark.parametrize("field", ["status","execution_authorised","candidate_evaluation_run","run_count_allowed",
    "experiment_version","implementation_commit","public_artifacts","private_commitments","private_lock_sha256",
    "protocol_sha256","intended_case_counts","intended_views","intended_embedding_model","python","dependencies","outputs"])
def test_missing_lock_field_rejected(formal_fixture,field):
    f=formal_fixture;del f["lock"][field];f["sync"]()
    with pytest.raises(ValueError,match="Missing"):checked(f)


@pytest.mark.parametrize("field,value", [("run_count_allowed",2),("run_count_allowed",True),("execution_authorised",False),
    ("candidate_evaluation_run",True),("status","runner_validated_pending_lock"),("experiment_version","another-version"),
    ("score_tolerance",{"absolute":.001,"relative":0}),("intended_case_counts",{"production":1,"diagnostic":16}),
    ("intended_embedding_model","another-model")])
def test_invalid_authorisation_or_contract_rejected(formal_fixture,field,value):
    f=formal_fixture;f["lock"][field]=value;f["sync"]()
    with pytest.raises(ValueError):checked(f)


def test_candidate_manifest_never_authorises_execute(formal_fixture):
    f=formal_fixture
    with pytest.raises(ValueError,match="Only pre_run_lock"):
        e.execute_evaluation(root=f["root"],lock_path=f["root"]/e.CANDIDATE_PATH,private_lock_path=f["private_path"],
            experiment_version=e.EXPERIMENT_VERSION,confirm=e.CONFIRM_EXECUTION,git=f["git"])


@pytest.mark.parametrize("path", [e.SELECTOR_PATH,"experiments/temporal_state_retrieval/scoring.py",
    "experiments/temporal_state_retrieval/baseline.py","tests/fixtures/temporal_state_metadata/freeze_manifest.json", e.RUNNER_PATH])
def test_frozen_and_implementation_hash_drift_rejected(formal_fixture,path):
    f=formal_fixture;save(f["root"]/path,b"changed")
    with pytest.raises(ValueError,match="hash"):checked(f)


@pytest.mark.parametrize("path", [e.RUNNER_PATH,
    "project_knowledge/process/experiments/temporal_state_retrieval/phase_3b_implementation_review.md"])
def test_b2_implementation_changes_bind_to_new_commit_not_parent(formal_fixture,path):
    f=formal_fixture
    save(f["root"]/path,b"synthetic revised B2 implementation")
    f["git"].committed[path]=(f["root"]/path).read_bytes()
    for item in f["lock"]["public_artifacts"]:
        if item["path"]==path:item["sha256"]=e.digest(f["root"]/path)
    f["sync"]()
    assert checked(f)["lock"]["implementation_commit"]==f["git"].implementation


@pytest.mark.parametrize("change", ["ancestor","post_implementation_file","lock_not_committed","same_head"])
def test_git_ancestry_and_exact_lock_only_diff(formal_fixture,change):
    f=formal_fixture;g=f["git"]
    if change=="ancestor":g.is_ancestor=False
    elif change=="post_implementation_file":g.changes+="\nM\tsrc/retrieval.py"
    elif change=="same_head":g.head=g.implementation
    else:g.lock_bytes=b"different"
    with pytest.raises(ValueError):checked(f)


@pytest.mark.parametrize("target", ["state","public_result","case_traces"])
def test_existing_state_or_output_rejects_preflight(formal_fixture,target):
    f=formal_fixture
    path=f["output"]/"execution_state.json" if target=="state" else f["output"]/"case_traces" if target=="case_traces" else f["root"]/e.PUBLIC_DIRECTORY/"candidate_aggregate_results.json"
    save(path,b"existing")
    with pytest.raises(ValueError,match="Existing"):checked(f)


class FakeClock:
    def __init__(self):self.n=0
    def tick(self):self.n+=1;return self.n/1000
    def utc(self):return "2000-01-01T00:00:00+00:00"


class ObservedWriter(e.AtomicWriter):
    def __init__(self):self.events=[];self.fail_case=False
    def write(self,path,value,**kwargs):
        if self.fail_case and Path(path).parent.name=="case_traces":raise OSError("synthetic publication failure")
        super().write(path,value,**kwargs)
        self.events.append((Path(path).name,copy.deepcopy(value)))


def synthetic_case(cid,context,section,tier,project):
    return dict(case_id=cid,project_id=project,context_id=context,section_id=section,benchmark_tier=tier,
        expected_support_status="supported",section_applicability="applicable",required_evidence_roles=["current_direction"],
        acceptable_gold_passages=[context+"-aim"],required_context_passages=[],expected_temporal_status=["current"],
        role_temporal_requirements={"current_direction":["current"]},acceptable_pair_sets=[],
        applicability_evidence_sets=[[context+"-aim"]],boundary_passages=[],excluded_or_misleading_passages=[],current_claim_roles=["current_direction"])


class FakeDependencies:
    synthetic=True
    def __init__(self,context):
        self.context=context;self.clock=FakeClock();self.writer=ObservedWriter();self.events=[]
        self.fail=None;self.score_count=0;self.request_count=0
        self.activity={"model_loads":0,"document_encode_calls":0,"query_encode_calls":0,"encode_calls":0,
            "openai_requests":0,"llm_calls":0,"summary_calls":0}
        self.environment={"device":"fake","logical_cpu_count":1,"torch_threads":1}
        self.data={"cases":[],"passages":[]}
        projects={"echo_documented_snapshot":"sample_echo_field","p96_final_documented":"synthetic_archive","signal_closed":"synthetic_loom"}
        for view,prefix in (("echo_documented_snapshot","EF"),("p96_final_documented","RS"),("signal_closed","SY")):
            for i,section in enumerate(e.SECTIONS,1):
                self.data["cases"].append(synthetic_case(f"{prefix}-{i:02}",view,section,"production",projects[view]))
        reqs=[(v,s) for v in e.VIEW_RECORDS for s in e.SECTIONS]
        for i,(view,section) in enumerate(reqs[:16],1):
            self.data["cases"].append(synthetic_case(f"DG-{i:02}",view,section,"diagnostic",projects.get(view,"synthetic_loom")))
        self.private_ids={c["case_id"] for c in self.data["cases"] if c["case_id"].startswith("RS")}
        self.traces={}
        for view in e.VIEW_RECORDS:
            self.data["passages"].append(dict(passage_id=view+"-aim",context_id=view,source="invented.md",quote="Aim",
                locator={"start_char":0,"end_char":3},temporal_status="current",evidence_role=["current_direction"],context_spans=[],inapplicability_case_ids=[]))
            for section in e.SECTIONS:
                item=dict(chunk_id="synthetic-a",source="invented.md",category="process",score=.5,excerpt="Aim",
                    start_char=0,end_char=3,visible_token_spans=[[0,3]],context_metadata=[])
                self.traces[view+"|"+section]={"selected_evidence":[item],"ordered_evidence":[item],
                    "queries":[{"query":q,"eligible_results":[item]} for q in ("synthetic first","synthetic second")]}
        passages={p["passage_id"]:p for p in self.data["passages"]}
        self.baseline_results=[scoring.score_case(c,passages,self.traces[c["context_id"]+"|"+c["section_id"]]) for c in self.data["cases"]]

    def activate(self,context):
        assert (context["output"]/"execution_state.json").exists()
        self.events.append("activate")
        if self.fail=="activate":raise RuntimeError("synthetic pre-score error")
    def model_loader(self,path):self.events.append("model");self.activity["model_loads"]+=1;return object()
    def prepare_views(self,context,model):
        self.events.append("views");self.activity["document_encode_calls"]+=4
        return {v:v for v in e.VIEW_RECORDS},{v:{"documents":n[0],"chunks":n[1]} for v,n in e.VIEW_SIZES.items()}
    def frozen_traces(self,context):
        return {"traces":copy.deepcopy(self.traces),"case_results":self.baseline_results,
            "case_keys":{c["case_id"]:[c["context_id"],c["section_id"]] for c in self.data["cases"]}}
    @contextmanager
    def selector(self):
        self.events.append("selector_open")
        try:yield object()
        finally:self.events.append("selector_closed")
    def request(self,view,section,frozen,selector):
        self.request_count+=1;self.activity["query_encode_calls"]+=2
        if self.fail=="candidate":raise ValueError("Candidate identity mismatch")
        return copy.deepcopy(self.traces[view+"|"+section]),dict(total_ms=3,selector_overhead_ms=1,
            query_encode_ms=1,retrieval_and_baseline_selection_ms=1.5,baseline_selection_ms=.5,retrieval_ms=1,excerpt_ms=.5)
    def load_gold(self,context):
        assert self.request_count==24*32 and self.events[-1]=="selector_closed"
        assert (context["output"]/"selection_trace.json").exists()
        self.events.append("gold");return self.data,self.private_ids
    def scorer(self,case,passages,trace):
        assert "gold" in self.events
        if self.fail=="second_score" and self.score_count==1:raise RuntimeError("synthetic partial-score error")
        self.score_count+=1;return scoring.score_case(case,passages,trace)


def test_full_synthetic_lifecycle_order_tiers_clock_and_durable_case_counts(formal_fixture):
    f=formal_fixture;context=checked(f);deps=FakeDependencies(context)
    result=e._run_once(context,deps)
    assert result["status"]=="execution_completed" and result["scored_case_count"]==34
    assert result["started_at"]=="2000-01-01T00:00:00+00:00"
    assert deps.request_count==768 and deps.score_count==34
    events=deps.writer.events
    for i,(name,data) in enumerate(events):
        if name=="execution_state.json" and data["scored_case_count"] and data["status"]=="execution_started":
            assert events[i-1][0].endswith(".json") and events[i-1][0]!="execution_state.json"
            assert "result" in events[i-1][1]
    agg=e.read_json(f["root"]/e.PUBLIC_DIRECTORY/"candidate_aggregate_results.json")
    assert agg["tiers"]["production"]["case_count"]==18 and agg["tiers"]["diagnostic"]["case_count"]==16
    assert not any(p.name=="failure_log.json" for p in f["output"].iterdir())
    with pytest.raises(FileExistsError):e._run_once(context,FakeDependencies(context))


@pytest.mark.parametrize("failure,count,status",[("activate",0,"execution_failed_before_scoring"),
    ("candidate",0,"execution_failed_before_scoring"),("second_score",1,"execution_failed_after_partial_scoring")])
def test_failure_is_durable_never_retried(formal_fixture,failure,count,status):
    f=formal_fixture;context=checked(f);deps=FakeDependencies(context);deps.fail=failure
    with pytest.raises((RuntimeError,ValueError)):e._run_once(context,deps)
    state=e.read_json(f["output"]/"execution_state.json")
    assert state["status"]==status and state["scored_case_count"]==count
    assert (f["output"]/"failure_log.json").exists()
    with pytest.raises(FileExistsError):e._run_once(context,FakeDependencies(context))
    if not count:assert "gold" not in deps.events


def test_case_publication_failure_consumes_run_and_preserves_pending_score(formal_fixture):
    f=formal_fixture;context=checked(f);deps=FakeDependencies(context);deps.writer.fail_case=True
    with pytest.raises(OSError,match="publication"):e._run_once(context,deps)
    failure=e.read_json(f["output"]/"failure_log.json")
    assert failure["scored_case_count"]==1 and failure["pending_case"]["result"]["case_id"]=="EF-01"
    assert e.read_json(f["output"]/"execution_state.json")["status"]=="execution_failed_after_partial_scoring"


def test_atomic_results_and_state_refuse_overwrite(tmp_path):
    writer=e.AtomicWriter();path=tmp_path/"result.json"
    writer.write(path,{"value":1})
    before=path.read_bytes()
    with pytest.raises(FileExistsError):writer.write(path,{"value":2})
    assert path.read_bytes()==before
    assert list(tmp_path.iterdir())==[path]


@pytest.mark.parametrize("value", [{"excerpt":"private words"},{"gold_labels":[]},{"summary":"private text"},
    {"note":"RS-01"},{"note":"P96"},{"note":"private_data/secret"},{"path":"anything"}])
def test_public_writer_rejects_private_structures(tmp_path,value):
    with pytest.raises(ValueError):e.AtomicWriter().write(tmp_path/"public.json",value,public=True)
    assert not list(tmp_path.iterdir())


def test_recompute_is_trace_only_exact_and_non_overwriting(formal_fixture,monkeypatch):
    f=formal_fixture;context=checked(f);e._run_once(context,FakeDependencies(context))
    # Synthetic files have fake artifact bytes; use the committed frozen scorer's
    # actual bytes as a temporary fixture commitment, never as participant input.
    scorer_path="experiments/temporal_state_retrieval/scoring.py"
    save(f["root"]/scorer_path,Path(scoring.__file__).read_bytes())
    for x in f["lock"]["public_artifacts"]:
        if x["path"]==scorer_path:x["sha256"]=e.digest(f["root"]/scorer_path)
    f["sync"]()
    manifest=e.read_json(f["output"]/"private_run_manifest.json")
    manifest["lock_hash"]=e.digest(f["root"]/e.LOCK_PATH);save(f["output"]/"private_run_manifest.json",manifest)
    monkeypatch.setattr(e,"GitView",lambda root:f["git"])
    def forbidden(*a,**kw):raise AssertionError("Runtime dependency entered during recompute")
    monkeypatch.setattr(e,"DefaultDependencies",forbidden);monkeypatch.setattr(e,"SelectorProcess",forbidden)
    before=(f["root"]/e.PUBLIC_DIRECTORY/"candidate_aggregate_results.json").read_bytes()
    result=e.recompute(f["root"],f["output"])
    assert result["status"]=="verified" and result["case_count"]==34
    assert before==(f["root"]/e.PUBLIC_DIRECTORY/"candidate_aggregate_results.json").read_bytes()
    with pytest.raises(ValueError,match="overwrite"):e.recompute(f["root"],f["output"])


@pytest.mark.parametrize("damage", ["changed", "missing"])
def test_recompute_mismatch_preserves_original_and_marks_validation_failed(formal_fixture,monkeypatch,damage):
    f=formal_fixture;context=checked(f);e._run_once(context,FakeDependencies(context))
    path=f["root"]/e.PUBLIC_DIRECTORY/"candidate_aggregate_results.json"
    if damage=="changed":save(path,{"synthetic":"tampered"})
    else:path.unlink()  # Synthetic fixture only; never a formal output.
    before=path.read_bytes() if path.exists() else None
    monkeypatch.setattr(e,"GitView",lambda root:f["git"])
    result=e.recompute(f["root"],f["output"])
    assert result["status"]=="validation_failed"
    assert (path.read_bytes() if path.exists() else None)==before
    assert e.read_json(f["output"]/"execution_state.json")["status"]=="validation_failed"


def test_no_arguments_no_resume_and_real_repository_injection_rejected():
    with pytest.raises(RuntimeError,match="disabled"):e.execute_evaluation()
    with pytest.raises(TypeError):e.execute_evaluation(resume=True)
    with pytest.raises(ValueError,match="injection"):
        e.execute_evaluation(root=e.ROOT,lock_path=e.ROOT/e.LOCK_PATH,private_lock_path=e.ROOT/"private_data/synthetic",
            experiment_version=e.EXPERIMENT_VERSION,confirm=e.CONFIRM_EXECUTION,dependencies=object())


def test_import_remains_inert_in_fresh_process():
    script="""
import sys,os
before=(os.getcwd(),dict(os.environ),list(sys.path))
def guard(event,args):
 if event=='open' and isinstance(args[1],str) and any(x in args[1] for x in 'wax+'):raise AssertionError('write')
 if event.startswith('socket.') or event=='subprocess.Popen':raise AssertionError('runtime activity')
sys.addaudithook(guard)
import experiments.temporal_state_retrieval.state_aware_experiment
assert before==(os.getcwd(),dict(os.environ),list(sys.path))
assert not any(x in sys.modules for x in ('torch','sentence_transformers','openai','retrieval'))
print('INERT')
"""
    result=subprocess.run([sys.executable,"-B","-c",script],capture_output=True,text=True,check=True,timeout=15)
    assert result.stdout.strip()=="INERT"


def test_persistent_worker_resources_close_without_runtime_imports():
    script="import sys,json\nprint('READY',flush=True)\nfor line in sys.stdin:\n print(json.dumps(['synthetic-a']),flush=True)"
    worker=e.SelectorProcess(command=[sys.executable,"-B","-u","-c",script],timeout=15)
    data={"section_id":"current_intention","ordered_eligible_candidates":[[{"chunk_id":"synthetic-a","record_id":"TT-R01","score":.5}]]*2,
          "eligible_record_states":{"TT-R01":"unknown"}}
    with worker:
        assert worker.select(data)==["synthetic-a"]
        assert worker.select(data)==["synthetic-a"]
    assert worker.process.poll()==0
    assert worker.process.stdin.closed and worker.process.stdout.closed and worker.errors.closed
    assert all(not t.is_alive() for t in worker.pool._threads)


@pytest.mark.parametrize("mutation",["order","score","category","count","query"])
def test_candidate_drift_fails_before_selector_or_gold(mutation):
    rows=[dict(chunk_id=n,source="synthetic",category="process",score=.5) for n in ("a","b")]
    frozen=[{"query":"one","eligible_results":rows}];current=copy.deepcopy(frozen)
    if mutation=="order":current[0]["eligible_results"].reverse()
    elif mutation=="count":current[0]["eligible_results"].pop()
    elif mutation=="query":current[0]["query"]="changed"
    else:current[0]["eligible_results"][0][mutation]=.4 if mutation=="score" else "feedback"
    with pytest.raises(ValueError):e.compare_candidates(current,frozen)


def test_exclusive_state_creation_under_concurrent_attempts(formal_fixture):
    context=checked(formal_fixture);barrier=threading.Barrier(2)
    def start():
        state=e.ExecutionState(context,e.AtomicWriter(),FakeClock());barrier.wait()
        try:state.start();return "created"
        except FileExistsError:return "refused"
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures=[executor.submit(start) for _ in range(2)]
        assert sorted(f.result(timeout=5) for f in futures)==["created","refused"]
    state=e.read_json(context["output"]/"execution_state.json")
    assert state["status"]=="execution_started" and state["scored_case_count"]==0


def test_worker_timeout_kills_reaps_closes_and_joins_without_sleep():
    # The child blocks on stdin EOF, not a timing sleep. Timeout must reap it.
    script="import sys\nprint('READY',flush=True)\nsys.stdin.read()"
    worker=e.SelectorProcess(command=[sys.executable,"-B","-u","-c",script],timeout=1)
    data={"section_id":"current_intention","ordered_eligible_candidates":[[],[]],"eligible_record_states":{}}
    with pytest.raises(TimeoutError):
        with worker:worker.select(data)
    assert worker.process.poll() is not None
    assert worker.process.stdin.closed and worker.process.stdout.closed and worker.errors.closed
    assert all(not t.is_alive() for t in worker.pool._threads)


def test_default_dependencies_are_lazy_and_index_injection_preserves_encode_contract():
    deps=e.DefaultDependencies(clock=FakeClock())
    class Retriever:
        def __init__(self,*args):raise AssertionError("Must not construct another model")
        def retrieve(self,*args):raise AssertionError("No semantic retrieval in this test")
    calls=[]
    model=SimpleNamespace(encode=lambda *a,**kw:calls.append((a,kw)) or "synthetic matrix")
    deps.retrieval=SimpleNamespace(SemanticRetriever=Retriever)
    chunks=[SimpleNamespace(content="synthetic text")]
    index=deps.retriever_factory(chunks,model)
    assert isinstance(index,Retriever) and index.model is model and index.chunks is chunks
    assert index.chunk_embeddings=="synthetic matrix"
    assert calls==[((['synthetic text'],),dict(convert_to_numpy=True,normalize_embeddings=True,show_progress_bar=False))]
    assert all(v==0 for v in deps.activity.values())


def test_default_request_checks_channels_before_adapter_or_selector():
    deps=e.DefaultDependencies(clock=FakeClock())
    deps.encode_ms=0
    row=SimpleNamespace(score=.5,chunk=SimpleNamespace(chunk_id="synthetic-a",source="synthetic.md",category="process",content="Aim"))
    class Recorder:
        def __init__(self,delegate):self.delegate=delegate;self.calls=[]
        def retrieve(self,query,top_k):
            value=self.delegate.retrieve(query,top_k);self.calls.append((query,value));return value
    calls=[]
    def select(definition,retriever,total_chunks,limit):
        for q in ("first","second"):retriever.retrieve(q,total_chunks)
        return [row]
    deps.b=SimpleNamespace(RecordingRetriever=Recorder)
    deps.production=SimpleNamespace(retrieve_diverse_evidence=select,select_evidence=lambda rows,*a,**kw:rows)
    deps.definitions={"current_intention":SimpleNamespace(preferred_categories=("process",))}
    index=SimpleNamespace(retrieve=lambda q,k:[row])
    deps.candidate_adapter=lambda *a,**kw:calls.append("adapter")
    selector=SimpleNamespace(select=lambda *a:calls.append("selector"))
    frozen={"queries":[{"query":"different","eligible_results":[]}],"selected_evidence":[]}
    with pytest.raises(e.CandidateMismatch):
        deps.request(dict(index=index,count=1),"current_intention",frozen,selector)
    assert calls==[]


def test_default_request_preserves_original_scores_and_times_selector_ipc():
    deps=e.DefaultDependencies(clock=FakeClock());deps.encode_ms=0
    rows=[SimpleNamespace(score=x,chunk=SimpleNamespace(chunk_id=n,source="synthetic.md",category="process",content=n)) for n,x in (("a",.8),("b",.6))]
    class Recorder:
        def __init__(self,delegate):self.delegate=delegate;self.calls=[]
        def retrieve(self,query,top_k):
            r=self.delegate.retrieve(query,top_k);self.calls.append((query,r));return r
    def select(d,r,total_chunks,limit):
        r.retrieve("first",total_chunks);r.retrieve("second",total_chunks);return rows
    def visible(r,raw):return dict(chunk_id=r.chunk.chunk_id,score=r.score,excerpt=r.chunk.content)
    deps.b=SimpleNamespace(RecordingRetriever=Recorder,visible_evidence=visible,
        ordered_trace=lambda items,*a:dict(selected_evidence=items,ordered_evidence=items))
    deps.production=SimpleNamespace(retrieve_diverse_evidence=select,select_evidence=lambda r,*a,**kw:r,create_excerpt=lambda t:t)
    deps.definitions={"current_intention":SimpleNamespace(preferred_categories=("process",))}
    projected={"section_id":"current_intention","ordered_eligible_candidates":[[],[]],"eligible_record_states":{}}
    deps.candidate_adapter=lambda *a,**kw:(projected,{"missing_metadata_count":0})
    payloads=[]
    selector=SimpleNamespace(select=lambda p:payloads.append(p) or ["b","a"])
    frozen={"queries":[{"query":q,"eligible_results":[dict(chunk_id=r.chunk.chunk_id,source=r.chunk.source,category="process",score=r.score) for r in rows]} for q in ("first","second")],
            "selected_evidence":[dict(chunk_id=r.chunk.chunk_id) for r in rows]}
    view=dict(index=SimpleNamespace(retrieve=lambda q,k:rows),count=2,source_records={},metadata=[],ids=set(),raw={"synthetic.md":"invented"})
    trace,timing=deps.request(view,"current_intention",frozen,selector)
    assert payloads==[projected]
    assert [r["score"] for r in trace["selected_evidence"]]==[.6,.8]
    assert timing["total_ms"]==pytest.approx(timing["retrieval_and_baseline_selection_ms"]+timing["selector_overhead_ms"]+timing["excerpt_ms"])
    assert timing["baseline_selection_ms"]==pytest.approx(timing["retrieval_and_baseline_selection_ms"]-timing["retrieval_ms"])


def test_case_trace_exclusive_publication_never_increments_twice(formal_fixture):
    context=checked(formal_fixture);state=e.ExecutionState(context,e.AtomicWriter(),FakeClock());state.start()
    result={"case_id":"EF-01"};trace={"synthetic":True}
    state.record(trace,result,baseline_result={},gold_case={})
    before=state.path.read_bytes()
    with pytest.raises(FileExistsError):state.record(trace,result,baseline_result={},gold_case={})
    assert state.path.read_bytes()==before and state.data["scored_case_count"]==1
