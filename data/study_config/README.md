# Local participant assignments

Copy [the safe example](../../config/participant_assignments.example.json) to `participant_assignments.json` in this directory only if no local configuration already exists. Edit the local copy to assign participant codes to distinct project IDs and project directories. Never overwrite existing assignments as part of setup.

The local JSON is excluded from Git. Only this README is allow-listed. Keep names and contact details out of display names and paths.

The participant server is bound to one code by `study_project_manager.py serve --participant P01`. Entering another code does not select or disclose another project. This is a supervised, loopback-only research tool, not an authenticated multi-user service; protect the local researcher account and do not expose it over a network.
