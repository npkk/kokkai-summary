import { createContext, useState, type ReactNode } from "react";

export interface SearchCriteria {
	session: number | null;
	nameOfMeeting: string | null;
	nameOfHouse: string[];
}

interface SearchContextType {
	searchCriteria: SearchCriteria | null;
	setSearchCriteria: (criteria: SearchCriteria | null) => void;
}

export const SearchContext = createContext<SearchContextType | undefined>(
	undefined,
);

export function SearchProvider({ children }: { children: ReactNode }) {
	const [searchCriteria, setSearchCriteria] = useState<SearchCriteria | null>(
		null,
	);

	return (
		<SearchContext.Provider value={{ searchCriteria, setSearchCriteria }}>
			{children}
		</SearchContext.Provider>
	);
}
