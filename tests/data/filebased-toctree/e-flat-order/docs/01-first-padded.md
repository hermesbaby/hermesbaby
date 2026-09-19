# Title of 01-first-padded

Leading zero: must still sort numerically as 1, i.e. before "2-second" and
"10-tenth", not lexically (which would put it between "01" and "10" only by
luck; the real risk is e.g. "09" vs "10" sorting as "09" < "10" numerically
but "10" < "09" would be wrong if compared as plain strings char-by-char
past the first digit run only when lengths differ, e.g. "2" vs "10").
