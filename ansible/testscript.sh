# no shebang for all posix shells
python3 app.py -b rcpscript.txt

echo "Tests" > tests.log.txt
for i in 1 2 3; do
  if cmp -s "test$i.json" "tests/answer$i.json"; then
    echo " Passed test $i!" >> tests/log.txt
  else
    echo " Failed test $i!" >> tests/log.txt
    exit $i
  fi
done
