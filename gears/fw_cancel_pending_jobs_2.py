#! /usr/bin/env python3
"""Cancel pending Flywheel jobs for a specific gear across all projects.

Examples:
	python fw_cancel_pending_jobs_2.py --gear-name file-classifier --dry-run
	python fw_cancel_pending_jobs_2.py --gear-name file-classifier --group d3b
	python fw_cancel_pending_jobs_2.py --gear-name file-classifier --group d3b --max-cancel 10
"""

import argparse
import os

import flywheel


def job_in_group(fw, job, group_id):
	if not group_id:
		return True

	parent_group = getattr(getattr(job, "parents", None), "group", None)
	if parent_group == group_id:
		return True

	destination = getattr(job, "destination", None)
	if not destination:
		return False

	try:
		dest_container = fw.get(destination.id)
	except Exception:
		return False

	return getattr(getattr(dest_container, "parents", None), "group", None) == group_id


def cancel_pending_jobs(fw, gear_name, group_id=None, dry_run=False, max_cancel=None):
	pending_jobs = fw.jobs.find("state=pending", f"gear_info.name={gear_name}", limit=max_cancel)

	seen = set()
	inspected = 0
	matched = 0
	cancelled = 0

	for job in pending_jobs:
		inspected += 1
		if not job_in_group(fw, job, group_id):
			continue

		matched += 1
		if job.id in seen:
			continue

		seen.add(job.id)
		destination = getattr(job, "destination", None)
		destination_type = getattr(destination, "type", "unknown")
		destination_id = getattr(destination, "id", "unknown")

		print(f"pending job: {job.id} | destination={destination_type}:{destination_id}")

		if dry_run:
			continue

		if max_cancel is not None and cancelled >= max_cancel:
			print(f"Reached --max-cancel={max_cancel}; stopping early.")
			break

		try:
			fw.get_job(job.id).change_state("cancelled")
			cancelled += 1
			print(f"  cancelled: {job.id}")
		except Exception as exc:
			print(f"  failed to cancel {job.id}: {exc}")

	return inspected, matched, cancelled


def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--gear-name", required=True, help="Flywheel gear name")
	parser.add_argument(
		"--group",
		default=None,
		help="Flywheel group ID to scope cancellations. Omit to run across all groups.",
	)
	parser.add_argument(
		"--dry-run",
		action="store_true",
		help="List pending jobs that would be cancelled without changing state.",
	)
	parser.add_argument(
		"--max-cancel",
		type=int,
		default=None,
		help="Optional safety limit for number of jobs to cancel.",
	)
	args = parser.parse_args()

	api_key = os.getenv("FW_API_KEY")
	if not api_key:
		raise RuntimeError("FW_API_KEY environment variable is required")

	fw = flywheel.Client(api_key)
	print("Flywheel Instance:", fw.get_config().site.api_url)
	print(
		f"Searching for pending jobs | gear={args.gear_name} | group={args.group or 'ALL'} | dry_run={args.dry_run}"
	)

	inspected, matched, cancelled = cancel_pending_jobs(
		fw,
		gear_name=args.gear_name,
		group_id=args.group,
		dry_run=args.dry_run,
		max_cancel=args.max_cancel,
	)

	print("--- summary ---")
	print(f"inspected pending jobs: {inspected}")
	print(f"matched scope: {matched}")
	print(f"cancelled: {cancelled}")


if __name__ == "__main__":
	main()

