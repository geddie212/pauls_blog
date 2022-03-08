SQL = 'postgres://fkmxqrweeufgyp:ef0c990ea186ff637e81050e38cc5a14692f6438195394e446b6b18b185e99ab@ec2-52-70-186-184.compute-1.amazonaws.com:5432/d5nm98be1hkdf4'.split('postgres')
SQL[0] += 'postgresql'
updated_SQL = f'{SQL[0]}{SQL[1]}'
print(updated_SQL)