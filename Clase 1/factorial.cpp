#include <iostream>
//factorial
using namespace std;
int main(){
	int num1, factorial=1;
	cout << "Introduce un numero para calcular su factorial: ";
	cin >> num1;
	for (int i = 1; i<=num1; i++){
		factorial *= i;
	}
	cout << "El factorial es: " << factorial;
	return 0;
}

