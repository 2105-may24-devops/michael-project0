# no shebang for all posix shells
/venv/bin/python3 app.py rcpscript.txt

for i in 1 2 3; do
  if cmp -s "test$i.json" "tests/answer$i.json"; then
    echo "Passed test $i!" > tests/log.txt
  else
    echo "Failed test $i!" > tests/log.txt
  fi
done