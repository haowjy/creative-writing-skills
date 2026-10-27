"""Presentation adapter; application services are independently callable."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
import uuid

from .index import Diagnostic, parse_index, resolve
from .interruptions import cancellable
from .storage import Draft, commit, edit_draft, load_index


def command_error(args, error):
    """Add known request context without echoing payloads or raw exceptions."""
    result = error.as_dict()
    result["operation"] = result["operation"] or " ".join(
        part for part in (args.command, getattr(args, "action", "")) if part)
    result["source"] = result["source"] or str(args.index or getattr(args, "client", "") or "")
    result["context"] = {
        name: str(getattr(args, name)) for name in ("index", "profile", "operation")
        if getattr(args, name, None) is not None
    }
    source = getattr(args, "source", None)
    if source is not None:
        result["context"]["source_ids"] = source if isinstance(source, list) else [source]
    return dict(error=result)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="drive-sync")
    parser.add_argument("--index", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    auth = commands.add_parser("auth")
    auth_actions = auth.add_subparsers(dest="action", required=True)
    for name in ("login", "status", "logout", "pick-folder"):
        action = auth_actions.add_parser(name)
        action.add_argument("--profile", default="personal")
        action.add_argument("--config-home", type=Path)
        if name in ("login", "pick-folder"):
            action.add_argument("--client", type=Path, required=True)
            action.add_argument("--port", type=int, default=8765)
    source = commands.add_parser("source")
    source_actions = source.add_subparsers(dest="action", required=True)
    rebind = source_actions.add_parser("rebind")
    rebind.add_argument("--source", required=True)
    rebind.add_argument("--root", required=True)
    rebind.add_argument("--path", required=True)
    rebind.add_argument("--state-home", type=Path)
    rebind.add_argument("--config-home", type=Path)
    rebind.add_argument("--apply", action="store_true")
    rebind.add_argument("--plan-digest")
    return_review = source_actions.add_parser("preview-return")
    return_review.add_argument("--source", required=True)
    return_review.add_argument("--state-home", type=Path)
    return_review.add_argument("--config-home", type=Path)
    return_review.add_argument("--accept-remote", action="store_true", help="Preview the explicit accept-remote conflict candidate; does not apply it")
    state = commands.add_parser("state")
    state_actions = state.add_subparsers(dest="action", required=True)
    recovery = state_actions.add_parser("recover")
    recovery.add_argument("--state-home", type=Path)
    recovery.add_argument("--config-home", type=Path)
    closure = state_actions.add_parser("close-unchanged")
    closure.add_argument("--operation", required=True)
    closure.add_argument("--state-home", type=Path)
    closure.add_argument("--config-home", type=Path)
    closure.add_argument("--apply", action="store_true")
    closure.add_argument("--plan-digest")
    resume = state_actions.add_parser("resume-batches")
    resume.add_argument("--operation", required=True)
    resume.add_argument("--state-home", type=Path)
    resume.add_argument("--config-home", type=Path)
    resume.add_argument("--apply", action="store_true")
    resume.add_argument("--plan-digest")
    batch_repair = state_actions.add_parser("repair-batches")
    batch_repair.add_argument("--operation", required=True)
    batch_repair.add_argument("--state-home", type=Path)
    batch_repair.add_argument("--config-home", type=Path)
    batch_repair.add_argument("--apply", action="store_true")
    batch_repair.add_argument("--plan-digest")
    repair = state_actions.add_parser("repair-created-layout")
    repair.add_argument("--operation", required=True)
    repair.add_argument("--state-home", type=Path)
    repair.add_argument("--config-home", type=Path)
    repair.add_argument("--apply", action="store_true")
    repair.add_argument("--plan-digest")
    content_repair = state_actions.add_parser("repair-created-content")
    content_repair.add_argument("--operation", required=True)
    content_repair.add_argument("--state-home", type=Path)
    content_repair.add_argument("--config-home", type=Path)
    content_repair.add_argument("--apply", action="store_true")
    content_repair.add_argument("--plan-digest")
    missing = state_actions.add_parser("acknowledge-missing")
    missing.add_argument("--source", required=True)
    missing.add_argument("--state-home", type=Path)
    missing.add_argument("--apply", action="store_true")
    missing.add_argument("--plan-digest")
    rebaseline = state_actions.add_parser("rebaseline")
    rebaseline.add_argument("--source", required=True)
    rebaseline.add_argument("--state-home", type=Path)
    rebaseline.add_argument("--config-home", type=Path)
    rebaseline.add_argument("--apply", action="store_true")
    rebaseline.add_argument("--plan-digest")
    conflict = commands.add_parser("conflict")
    conflict_actions = conflict.add_subparsers(dest="action", required=True)
    inspect = conflict_actions.add_parser("inspect")
    inspect.add_argument("--source", required=True)
    inspect.add_argument("--state-home", type=Path)
    inspect.add_argument("--config-home", type=Path)
    resolution = conflict_actions.add_parser("resolve")
    resolution.add_argument("--source", required=True)
    resolution.add_argument("--choice", choices=["keep-local", "accept-remote", "restore-layout", "replace-storage"], required=True)
    resolution.add_argument("--apply", action="store_true")
    resolution.add_argument("--plan-digest")
    resolution.add_argument("--state-home", type=Path)
    resolution.add_argument("--config-home", type=Path)
    sync = commands.add_parser("sync")
    sync.add_argument("--apply", action="store_true")
    sync.add_argument("--folders-only", action="store_true", help="Plan/apply only mirrored folder creation")
    sync.add_argument("--initialize", action="store_true", help="Create verified empty Doc identities, not completed reading copies")
    sync.add_argument("--plan-digest")
    sync.add_argument("--source", action="append", help="Sync this source UUID and required parents; repeat for multiple items")
    sync.add_argument("--state-home", type=Path)
    sync.add_argument("--config-home", type=Path)
    conversion = commands.add_parser("conversion")
    conversion_actions = conversion.add_subparsers(dest="action", required=True)
    conversion_actions.add_parser("check")
    conversion_actions.add_parser("capabilities")
    index = commands.add_parser("index")
    actions = index.add_subparsers(dest="action", required=True)
    create = actions.add_parser("create")
    create.add_argument("--profile", default="personal")
    for name in ("show", "validate", "preview"):
        actions.add_parser(name)
    edit = actions.add_parser("edit")
    edit.add_argument("--edits", required=True, help="JSON list of {operation,path,value} edits; path is a list of mapping keys")
    edit.add_argument("--expected-digest", required=True)
    edit.add_argument("--save", action="store_true", help="Save configuration only; never sync")
    args = parser.parse_args(argv)
    # Invalid authorization requests must fail before loading credentials or
    # making remote reads. These are presentation constraints, not sync rules.
    if getattr(args, "apply", False) and not args.plan_digest:
        parser.error("--apply requires the reviewed --plan-digest")
    if args.command == "sync" and args.initialize and args.folders_only:
        parser.error("--initialize and --folders-only are mutually exclusive")
    try:
        if args.command == "auth":
            from .auth import begin_login, complete_login, begin_pick_folder, complete_pick_folder, auth_status, logout
            if args.action == "login":
                session = begin_login(args.profile, args.client, home=args.config_home, port=args.port)
                print(json.dumps(dict(event="open_browser", url=session.authorization_url)), flush=True)
                try:
                    output = complete_login(session)
                finally:
                    session.close()
            elif args.action == "pick-folder":
                session = begin_pick_folder(args.profile, args.client, home=args.config_home, port=args.port)
                print(json.dumps(dict(event="open_browser", url=session.authorization_url)), flush=True)
                try:
                    output = complete_pick_folder(session)
                finally:
                    session.close()
            elif args.action == "status":
                output = auth_status(args.profile, home=args.config_home)
            else:
                output = logout(args.profile, home=args.config_home)
            print(json.dumps(output, indent=2))
            return 0
        if args.command == "conversion" and args.action == "capabilities":
            from .capabilities import format_capabilities
            print(json.dumps(dict(formats=[asdict(c) for c in format_capabilities()]), indent=2))
            return 0
        if args.index is None:
            parser.error("--index is required for this command")
        if args.command == "source" and args.action == "preview-return":
            from .auth import authorized_session
            from .google import GoogleDrive
            from .return_review import preview_return
            loaded = load_index(args.index)
            with authorized_session(loaded.model.auth, home=args.config_home) as session:
                result = preview_return(args.index, GoogleDrive(session, loaded.model.id), args.source,
                                        home=args.state_home, accept_remote=args.accept_remote)
            print(json.dumps(asdict(result) | {'directory': str(result.directory)}, indent=2))
            return 0
        if args.command == "source":
            from .application import state_home
            from .state import StateStore
            from .rebind import plan_rebind, apply_rebind
            loaded = load_index(args.index)
            store = StateStore(args.state_home or state_home(), loaded.model.id)
            from .auth import authorized_session
            from .google import GoogleDrive
            with authorized_session(loaded.model.auth, home=args.config_home) as session:
                remote = GoogleDrive(session, loaded.model.id)
                with store.lock():
                    plan = plan_rebind(args.index, store, args.source, args.root, args.path, remote)
                if args.apply:
                    result = apply_rebind(plan, args.index, store, args.plan_digest, args.root, args.path, remote)
                    print(json.dumps(result, indent=2))
                else:
                    print(json.dumps(dict(plan=asdict(plan), digest=plan.digest), indent=2))
            return 0
        if args.command == "state" and args.action == "acknowledge-missing":
            from .application import state_home
            from .state import StateStore
            from .missing import missing_plan, acknowledge_missing
            loaded = load_index(args.index)
            store = StateStore(args.state_home or state_home(), loaded.model.id)
            if args.apply:
                print(json.dumps(acknowledge_missing(args.index, store, args.source, args.plan_digest), indent=2))
            else:
                with store.lock():
                    plan = missing_plan(args.index, store, args.source)
                print(json.dumps(dict(plan=asdict(plan), digest=plan.digest), indent=2))
            return 0
        if args.command in ("state", "conflict"):
            from .application import recover_sync, state_home
            from .auth import authorized_session
            from .google import GoogleDrive
            from .state import StateStore
            from .conflicts import inspect_conflict
            loaded = load_index(args.index)
            with authorized_session(loaded.model.auth, home=args.config_home) as session:
                remote = GoogleDrive(session, loaded.model.id)
                if args.command == "state" and args.action in ("repair-created-layout", "repair-created-content"):
                    from .create_repair import repair_created_layout, repair_created_content
                    repair_service = repair_created_layout if args.action == "repair-created-layout" else repair_created_content
                    if args.apply:
                        result = cancellable(lambda token: repair_service(args.index, remote, args.operation,
                            args.plan_digest, home=args.state_home, cancellation=token))
                    else:
                        result = repair_service(args.index, remote, args.operation, home=args.state_home)
                    print(json.dumps(asdict(result) if args.apply else dict(plan=asdict(result), digest=result.digest), indent=2))
                    return 130 if args.apply and result.cancelled else 2 if args.apply and any(f.status != "verified" for f in result.files) else 0
                if args.command == "state" and args.action in ("resume-batches", "repair-batches"):
                    from .batch_resume import resume_batches
                    from .batch_repair import repair_batches
                    batch_service = resume_batches if args.action == "resume-batches" else repair_batches
                    if args.apply:
                        result = cancellable(lambda token: batch_service(args.index, remote,
                            args.operation, args.plan_digest, home=args.state_home, cancellation=token))
                        print(json.dumps(asdict(result), indent=2))
                        return 130 if result.cancelled else 2 if any(f.status not in ("verified", "noop") for f in result.files) else 0
                    plan = batch_service(args.index, remote, args.operation, home=args.state_home)
                    print(json.dumps(dict(plan=asdict(plan), digest=plan.digest), indent=2))
                    return 0
                if args.command == "state" and args.action == "close-unchanged":
                    from .unchanged import close_unchanged
                    result = close_unchanged(args.index,
                        StateStore(args.state_home or state_home(), loaded.model.id),
                        remote, args.operation, args.plan_digest if args.apply else None)
                    print(json.dumps(result if args.apply else dict(plan=asdict(result), digest=result.digest), indent=2))
                    return 0
                if args.command == "state" and args.action == "rebaseline":
                    from .rebaseline import plan_rebaseline, apply_rebaseline
                    store = StateStore(args.state_home or state_home(), loaded.model.id)
                    if args.apply:
                        result = apply_rebaseline(args.index, store, remote, args.source, args.plan_digest)
                        print(json.dumps(result, indent=2))
                        return 0
                    with store.lock():
                        store.bind_account(remote.identity)
                        plan = plan_rebaseline(args.index, store, remote, args.source)
                    print(json.dumps(dict(digest=plan.digest, source_id=plan.source_id, baseline=asdict(plan.baseline), old_binding_hash=plan.old_binding_hash), indent=2))
                    return 0
                if args.command == "state":
                    result = recover_sync(args.index, remote, home=args.state_home)
                elif args.action == "resolve":
                    from .application import resolve_reviewed
                    from .planner import Authorization
                    if args.apply:
                        authorization = Authorization(args.plan_digest, loaded.model.id, frozenset([args.source]), frozenset(["create", "push", "pull"]))
                        result = cancellable(lambda token: resolve_reviewed(args.index, remote, args.source, args.choice, authorization, home=args.state_home, cancellation=token))
                    else:
                        plan = resolve_reviewed(args.index, remote, args.source, args.choice, home=args.state_home)
                        print(json.dumps(dict(plan=asdict(plan), digest=plan.digest), indent=2))
                        return 0
                else:
                    result = inspect_conflict(StateStore(args.state_home or state_home(), loaded.model.id), remote, args.source)
                print(json.dumps(asdict(result), default=str, indent=2))
                return 130 if getattr(result, "cancelled", False) else 2 if hasattr(result, "files") and any(f.status != "verified" for f in result.files) else 0
        if args.command == "sync":
            from .application import preview_sync, combined_plan, apply_reviewed
            from .auth import authorized_session
            from .google import GoogleDrive
            from .planner import Authorization
            scope = frozenset(args.source) if args.source else None
            loaded = load_index(args.index)
            with authorized_session(loaded.model.auth, home=args.config_home) as session:
                remote = GoogleDrive(session, loaded.model.id)
                if args.initialize or args.folders_only:
                    from .application import initialize_documents, initialize_folders
                    initialize = initialize_folders if args.folders_only else initialize_documents
                    plan = initialize(args.index, remote, home=args.state_home, source_ids=scope)
                    if args.apply:
                        auth = Authorization(args.plan_digest, plan.index_id, frozenset(o.source_id for o in plan.operations), frozenset(["create"]))
                        result = cancellable(lambda token: initialize(args.index, remote, auth, home=args.state_home, cancellation=token, source_ids=scope))
                        print(json.dumps(asdict(result), indent=2))
                        return 130 if result.cancelled else 0 if all(f.status in ("verified","noop") for f in result.files) else 2
                    print(json.dumps(dict(plan=asdict(plan),digest=plan.digest),indent=2))
                    return 0
                if args.apply:
                    # Scope/directions are bound by the supplied exact plan digest.
                    preview = preview_sync(args.index, remote, home=args.state_home, source_ids=scope)
                    plan = combined_plan(preview)
                    auth = Authorization(args.plan_digest, plan.index_id,
                                         frozenset(o.source_id for o in plan.operations),
                                         frozenset({"create", "push", "pull"}))
                    result = cancellable(lambda token: apply_reviewed(args.index, remote, auth, home=args.state_home, cancellation=token, source_ids=scope))
                    print(json.dumps(asdict(result), indent=2))
                    return 130 if result.cancelled else 0 if all(f.status in ("verified", "noop") for f in result.files) else 2
                plan = combined_plan(preview_sync(args.index, remote, home=args.state_home, source_ids=scope))
                print(json.dumps(dict(plan=asdict(plan), digest=plan.digest), indent=2))
                return 0
        if args.command == "conversion":
            from .capabilities import check_conversion
            reports = check_conversion(args.index)
            print(json.dumps(dict(reports=[asdict(report) for report in reports]), indent=2))
            return 0 if all(report.supported for report in reports) else 2
        if args.action == "create":
            raw = dict(version=1, kind="drive-sync", id=str(uuid.uuid4()), auth=args.profile,
                       roots={}, selection=dict(include=[], files=[], exclude=[]),
                       policy=dict(default_storage="google-doc", formats=["markdown", "text", "html", "epub"], overrides=[]))
            loaded = commit(args.index, Draft(raw), None)
            output = dict(index=loaded.raw, digest=loaded.digest)
        else:
            loaded = load_index(args.index)
            if args.action == "edit":
                from .storage import parse_edits
                edits = parse_edits(json.loads(args.edits))
                if args.expected_digest != loaded.digest:
                    raise Diagnostic("stale_index", "Index digest differs from the reviewed version.", "Reload and review again.")
                draft = edit_draft(loaded, edits)
                sources = resolve(parse_index(draft.raw), args.index)
                if args.save:
                    loaded = commit(args.index, draft, loaded.digest)
                output = dict(index=draft.raw, saved=args.save, digest=loaded.digest,
                              sources=[asdict(s) for s in sources])
            elif args.action == "preview":
                output = dict(digest=loaded.digest, sources=[asdict(s) for s in resolve(loaded.model, args.index)])
            else:
                output = dict(index=loaded.raw, digest=loaded.digest, valid=True)
        print(json.dumps(output, default=str, indent=2))
        return 0
    except Diagnostic as exc:
        print(json.dumps(command_error(args, exc)), file=sys.stderr)
        return 2
    except OSError:
        error = Diagnostic("local_io_error", "A requested local operation could not complete.",
            "Check the requested paths, permissions and available disk space. If a sync or repair was applying, inspect state and run state recover before attempting another write.")
        print(json.dumps(command_error(args, error)), file=sys.stderr)
        return 2
    except (ValueError, KeyError, TypeError):
        error = Diagnostic("invalid_request", "The request could not be parsed or validated.",
                           "Check command arguments and JSON edit syntax; use --help for the accepted shape.")
        print(json.dumps(command_error(args, error)), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
