#!/system/bin/sh
#
# Mirror Damru-baked extra system CAs into the live Conscrypt APEX store.
#
# /apex is mounted at boot, so files written there during a Docker commit are
# not durable. Keep the durable source in /system/etc/security/cacerts and copy
# only the filenames listed in damru-extra-ca.list after the APEX is available.

timeout="${1:-45}"
case "$timeout" in
    ''|*[!0-9]*) timeout=45 ;;
esac

system_dir="/system/etc/security/cacerts"
apex_dir="/apex/com.android.conscrypt/cacerts"
manifest="$system_dir/damru-extra-ca.list"

[ -f "$manifest" ] || exit 0

end=$(( $(date +%s) + timeout ))
while [ "$(date +%s)" -le "$end" ]; do
    if [ -d "$apex_dir" ]; then
        mount -o remount,rw /apex/com.android.conscrypt 2>/dev/null || \
            mount -o remount,rw /apex 2>/dev/null || true

        ok=1
        while IFS= read -r name || [ -n "$name" ]; do
            case "$name" in
                ''|*/*|*'..'*|*[!A-Za-z0-9._-]*)
                    continue
                    ;;
            esac
            src="$system_dir/$name"
            dst="$apex_dir/$name"
            if [ ! -f "$src" ]; then
                ok=0
                continue
            fi
            cp "$src" "$dst" 2>/dev/null || cat "$src" > "$dst" 2>/dev/null || {
                ok=0
                continue
            }
            chown root:root "$dst" 2>/dev/null || true
            chmod 0644 "$dst" 2>/dev/null || true
        done < "$manifest"

        [ "$ok" = "1" ] && exit 0
    fi
    sleep 1
done

exit 1
