# Source version locking

Resolve the source root for every release role first. Directory names are irrelevant; each root must be a Git worktree and contain the selected build entrypoint.

Fetch the remote and resolve a requested ref to a commit. With no ref supplied, use the remote's advertised default branch after fetch; do not use the current local branch.

```bash
lock_source() {
  role=$1
  source_dir=$2
  requested_ref=${3:-${SOURCE_REF:-}}
  source_dir=$(git -C "$source_dir" rev-parse --show-toplevel)
  git -C "$source_dir" fetch --prune origin
  if [ -z "$requested_ref" ]; then
    requested_ref=$(git -C "$source_dir" symbolic-ref --quiet --short refs/remotes/origin/HEAD)
  fi
  commit=$(git -C "$source_dir" rev-parse "${requested_ref}^{commit}")
  printf '%s ref=%s commit=%s source=%s\n' "$role" "$requested_ref" "$commit" "$source_dir"
}
```

Use `SOURCE_REF` for a release-wide ref. Use `STUDIO_SOURCE_REF`, `FRONTEND_SOURCE_REF`, `DESIGN_SOURCE_REF`, `OPS_SOURCE_REF`, or `IAM_SOURCE_REF` when a source role needs a different branch, tag, or SHA.

Create a temporary detached worktree for every resolved commit and build only from those worktrees. Retain the role/ref/SHA mapping alongside immutable image digests and, for Operations, use the exact locked Ops worktree as the migration source. If the remote default branch, requested ref, or commit cannot be resolved, stop rather than falling back to a local branch or uncommitted checkout.
