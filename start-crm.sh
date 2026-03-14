#!/bin/bash
# Start Next.js for CRM
# Called by launchd: ~/Library/LaunchAgents/com.thegrantscout.nextjs.plist
# Toggle DEV_MODE=1 for hot-reload during UI work, 0 for production

DEV_MODE=1

cd "/Users/aleckleinman/Documents/TheGrantScout/5. Operations/2. Website/thegrantscout-landing"

if [ "$DEV_MODE" = "1" ]; then
  exec /usr/local/bin/npm run dev
else
  if [ ! -d .next ] || [ package.json -nt .next/BUILD_ID ]; then
    /usr/local/bin/npm run build
  fi
  exec /usr/local/bin/npm start
fi
