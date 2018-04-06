# Things that need to be done on 4/7:

- [ ] Create a way to distinguish one Grid_Square Object from another
- [ ] Type up code that compares one square to another
- [ ] Type up code the algorithm that will match one square to another (from previous to current)

### PseudoCode for Algorithm:
```{python}
	update_squares(previous_squares, current_squares, current_position):
		possibleList = [:]
		finalListing = {i:None for i in a}

		for ps in previous_squares:
			for cs in current_squares
				possibleList[ps.name[0:1] + ps.name[0:1]] = compare(ps,cs)
		

		for flKey in finalListing:
			finalListing[flKey] = min([ps for ps in possibleList if flKey in ps], key = possibleList.get)
		
		return finalListing
		
